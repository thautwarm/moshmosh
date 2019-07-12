import ast

from syntax_rule import *


def compare(v1, op, v2):
    return ast.Compare(v1, [op], [v2])


def if_else(exp, br1, br2):
    return ast.If(exp, body=br1, orelse=br2)


def assign_name(name, val):
    return ast.Assign([ast.Name(name, ctx=ast.Store())], val)


def raise_not_match(_):
    """
    # TODO: more human-friendly error reporting
    """
    return ast.Raise(exc=ast.Name(id="MatchError", ctx=ast.Load()), cause=None)


class CaseCompilation(ast.NodeVisitor):
    """
    https://mail.python.org/pipermail/python-ideas/2015-April/032920.html

    with match(expr):
        if C(a, b): do_some1
        if _: do_some2
    =>
    .r0 = expr
    try:
        .r1 = C.__match__(.r0, 2)
        (.r2.a, .r3.b) = .r1
        a = .r2.a
        b = .r3.b
        do_some # with a and b
    except MatchError:
        try:
            r = .r0
        except:
            raise MatchError


            ...
    """
    def __init__(self, name_of_val_to_match, captures, block, pat: 'PatternMatching'):
        """
        :param captures: a dict maps mangling names to local names
        """
        self.name_of_val_to_match = name_of_val_to_match
        self.block = block # type: list
        self.pointer = None
        self.pat = pat
        self.captures = captures

    @property
    def val_to_match(self):
        return ast.Name(self.name_of_val_to_match, ctx=ast.Load())

    def visit_Num(self, v: ast.Num):
        self.visit_value(v.n)

    def visit_Str(self, v: ast.Str):
        self.visit_value(v.s)

    def visit_Name(self, v: ast.Name):
        self.captures[self.name_of_val_to_match] = v.id

    def visit_NameConstant(self, v: ast.NameConstant):
        self.visit_value(v.value)

    def visit_Constant(self, c: ast.Constant):
        self.visit_value(c.value)

    def visit_value(self, i):
        cond = compare(self.val_to_match, ast.NotEq(), ast.Constant(i))
        raise_ = raise_not_match(i)
        self.block.append(if_else(cond, [raise_], []))

    def visit_Call(self, call: ast.Call):
        """
        for constructors/recognizers
        """
        match = ast.Attribute(call.func, "__match__", ctx=ast.Load())
        matched = ast.Call(match, [self.val_to_match, ast.Constant(len(call.args))], keywords=[])
        ids = [self.pat.next_id for _ in call.args]
        lhs = ast.Tuple([ast.Name(id, ctx=ast.Store()) for id in ids], ctx=ast.Store())
        deconstruct = ast.Assign([lhs], matched, ctx=ast.Store())

        self.block.append(deconstruct)
        for id_, arg in zip(ids, call.args):
            CaseCompilation(id_, self.captures, self.block, self.pat).visit(arg)

class PatternMatching(ast.NodeTransformer):

    def __init__(self):
        def id_gen():
            i = 0
            while True:
                yield "PM%d.%d" % (id(self), i)
                i += 1
        self.local_id_generator = id_gen()

    @property
    def next_id(self):
        return next(self.local_id_generator)

    def visit_With(self, node: ast.With):
        # check if is the form:
        # ```
        # with case(_)
        # ```
        if not len(node.items):
            return self.generic_visit(node)

        item = node.items[0].context_expr
        if not isinstance(item, ast.Call):
            return self.generic_visit(node)

        fn = item.func
        if not isinstance(fn, ast.Name) or fn.id != "match":
            return self.generic_visit(node)

        # check if is `match(val)`
        assert not item.keywords and len(item.args) == 1
        # check if all stmts in the with block are in the form
        # `if <pattern>: stmts

        assert all(isinstance(stmt, ast.If) for stmt in node.body)

        val_to_match = item.args[0]
        name_of_val_to_match = self.next_id

        ifs = node.body # type: List[ast.If]
        def make_try_stmt(if_matched_br_, not_matched_br_):
            return ast.Try(
                    body=if_matched_br_,
                    handlers = [
                        ast.ExceptHandler(
                                type=ast.Name("MatchError", ctx=ast.Load()),
                                name=None,
                                body=not_matched_br_
                        ),
                    ],
                    orelse=[],
                    finalbody=[]
            )
        blocks = []

        for if_ in ifs:
            assert not if_.orelse # check if in the form of `if case: ...`
            captures = {}
            block = []
            case = if_.test
            case_compilation = CaseCompilation(name_of_val_to_match, captures, block, self)
            case_compilation.visit(case)
            for actual_name, local_bind_name in captures.items():
                block.append(assign_name(local_bind_name, ast.Name(actual_name, ctx=ast.Load())))
            block.extend(if_.body)
            blocks.append(block)
        blocks.reverse()

        # reduce
        last = [raise_not_match(None)]
        for each in blocks:
            last = [make_try_stmt(each, last)]

        return [assign_name(name_of_val_to_match, val_to_match), last[0]]


def pattern_matching(node):
    return PatternMatching().visit(node)