from io import StringIO
from moshmosh.ast_compat import ast
from moshmosh.ast_compat import ConsistentConstant
from moshmosh.extensions.pattern_matching.core import *
from moshmosh.extension import Extension, Activation
from moshmosh.extensions.pattern_matching.runtime import NotExhaustive
from moshmosh.ctx_fix import ExprContextFixer


class SyntacticPatternBinding:
    def __init__(self, case_comp: CaseCompilation):
        self.case_comp = case_comp

    def visit_Name(self, n: ast.Name):
        if n.id == "_":
            return self.case_comp.wildcard()
        return self.case_comp.capture(Symbol(n.id, n.lineno, n.col_offset))

    def visit_Call(self, n: ast.Call):
        if n.keywords:
            raise NotImplementedError(n)

        if isinstance(n.func, ast.Name):
            if n.func.id == 'pin' and len(
                n.args) == 1:
                return self.case_comp.pin(Expr(n.args[0]))
            if n.func.id == 'isinstance':
                if n.args == 1:
                    expr = Expr(n.args[0])
                else:
                    expr = Expr(ast.Tuple(n.args, ast.Load()))
                return self.case_comp.instance_of(expr)

        return self.case_comp.recog2(
            Expr(n.func), [self.visit(elt) for elt in n.args])

    def visit_BoolOp(self, n: ast.BoolOp):

        if isinstance(n.op, ast.And):
            cases = list(map(self.visit, n.values))
            return self.case_comp.intersect(cases)
        if isinstance(n.op, ast.Or):
            cases = list(map(self.visit, n.values))
            return self.case_comp.alternative(cases)

        raise NotImplementedError(n)

    def _visit_seq(self, type, n):
        def find_star(elts):
            for i, elt in enumerate(elts):
                if isinstance(elt, ast.Starred):
                    return i
            return -1
        star_idx = find_star(n.elts)
        if star_idx is -1:
            elts = list(map(self.visit, n.elts))
            return self.case_comp.seq_n(type, elts)

        ast_elts = n.elts
        elts1 = list(map(self.visit, ast_elts[:star_idx]))
        star = self.visit(ast_elts[star_idx].value)
        elts2 = list(map(self.visit, ast_elts[star_idx+1:]))
        return self.case_comp.seq_m_star_n(type, elts1, star, elts2)


    def visit_Tuple(self, n: ast.Tuple):
        return self._visit_seq(tuple, n)

    def visit_List(self, n: ast.List):
        return self._visit_seq(list, n)

    def visit(self, node):
        """Visit a node."""
        if isinstance(node, ConsistentConstant):
            return self.case_comp.literal(node)
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, None)
        if visitor is None:
            raise TypeError(node)
        return visitor(node)


class GenMatch(ast.NodeTransformer):
    def __init__(self, token: str, activation):
        self.token = token
        self.activation = activation

        def id_gen():
            i = 0
            while True:
                yield "PM%d.%d" % (id(self.activation), i)
                i += 1

        self.local_id_generator = id_gen()

    @property
    def next_id(self):
        return next(self.local_id_generator)

    def visit_With(self, node: ast.With):
        if node.lineno not in self.activation:
            return self.generic_visit(node)

        if not len(node.items):
            return self.generic_visit(node)

        item = node.items[0].context_expr
        if not isinstance(item, ast.Call):
            return self.generic_visit(node)

        fn = item.func
        if not isinstance(fn, ast.Name) or fn.id != self.token:
            return self.generic_visit(node)

        assert not item.keywords

        assert all(isinstance(stmt, ast.If) for stmt in node.body)

        if len(item.args) is not 1:
            val_to_match = ast.Tuple(item.args, ast.Load())
        else:
            val_to_match = item.args[0]

        cached = Symbol(self.next_id, node.lineno, node.col_offset).to_name()

        ifs = node.body  # type: t.List[ast.If]
        for if_ in ifs:
            assert not if_.orelse

        case_comp = CaseCompilation()
        spb = SyntacticPatternBinding(case_comp)

        pairs = []
        for if_ in ifs:
            case = spb.visit(if_.test)
            stmts = Stmts(if_.body)
            pairs.append((case, stmts))

        res = case_comp.match(pairs)(Expr(cached))
        suite = res.suite
        suite.reverse()
        suite.append(ast.Assign([cached], val_to_match))
        suite.reverse()
        return suite


class PatternMatching(Extension):
    __slots__ = ('tokens', )
    identifier = 'pattern-matching'

    def pre_rewrite_src(self, io: StringIO):
        io.write('from {} import {}\n'.format(__name__,
                                              NotExhaustive.__name__))

    def rewrite_ast(self, node: ast.AST):
        node = GenMatch(self.token, self.activation).visit(node)
        ExprContextFixer().visit(node)
        return node

    def __init__(self, token='match'):
        self.token = token
