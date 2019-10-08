import ast
from moshmosh.extension import Extension, Activation
from moshmosh.rewrite_helper import ast_to_literal
from moshmosh.ctx_fix import ExprContextFixer

runtime_ast_build = '_ast_build'
runtime_ast_copy = '_ast_copy'
_fix_ast_ctx = ExprContextFixer().visit

__all__ = ['build_ast']


def build_ast(d):
    nodes = literal_build_ast(d)
    nodes = fix_ast_ctx(nodes)

    mock = ast.Module(nodes)
    ast.fix_missing_locations(mock)
    return mock.body


def fix_ast_ctx(node):
    if isinstance(node, list):
        for each in node:
            fix_ast_ctx(each)
    else:
        _fix_ast_ctx(node)
    return node


def literal_build_ast(literal):
    """
    Convert a python literal to an AST.
    """
    if isinstance(literal, dict):
        ctor = literal.pop('constructor')
        ctor = getattr(ast, ctor)
        return ctor(**{k: literal_build_ast(v) for k, v in literal.items()})

    if isinstance(literal, list):
        res = []
        for each in literal:
            each = literal_build_ast(each)
            if isinstance(each, list):
                res.extend(each)
            elif isinstance(each, ast.Expr) and isinstance(each.value, list):
                res.extend(each.value)
            else:
                res.append(each)
        return res

    return literal


class Symbol:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return self.id

    def __iter__(self):
        yield self


class Splicing(ast.NodeTransformer):
    def __init__(self, syms):
        self.syms = {
            k: Symbol('{}({})'.format(runtime_ast_copy, k))
            for k in syms
        }

    def visit_Name(self, n: ast.Name):
        return self.syms.get(n.id, n)


class ArgumentCollector(ast.NodeVisitor):
    def __init__(self):
        self.args = set()

    def visit_arg(self, arg: ast.arg):
        self.args.add(arg.arg)


class MacroTransform(ast.NodeTransformer):
    def __init__(self, activation: Activation, token: str):
        self.activation = activation
        self.token = token

    def visit_FunctionDef(self, fn: ast.FunctionDef):
        if not len(fn.decorator_list) is 1:
            return self.generic_visit(fn)
        deco = fn.decorator_list[0]

        if not (isinstance(deco, ast.Name) and deco.id == self.token):
            return self.generic_visit(fn)

        assert fn.body
        fn.decorator_list.pop()
        arg_collector = ArgumentCollector()
        arg_collector.visit(fn)
        args = arg_collector.args
        splicing = Splicing(args)

        body_head = fn.body[-1]
        lineno, col_offset = body_head.lineno, body_head.col_offset
        new_body = []
        for stmt in fn.body:
            stmt = splicing.visit(stmt)
            new_body.append(stmt)

        mod: ast.Module = ast.parse(repr(ast_to_literal(new_body)))
        ast.fix_missing_locations(mod)
        expr: ast.Expr = mod.body[0]
        value = expr.value
        fn.body = [
            ast.Return(
                ast.Call(ast.Name(runtime_ast_build, ast.Load()), [value], []),
                lineno=lineno,
                col_offset=col_offset)
        ]
        return fn


class Template(Extension):

    __slots__ = ('activation', )
    identifier = "template-python"
    activation: Activation

    def __init__(self, token="quote"):
        self.activation = Activation()
        self.token = token

    def pre_rewrite_src(self, io):
        io.write('from {} import build_ast as {}\n'.format(
            __name__, runtime_ast_build))
        io.write('from copy import deepcopy as {}\n'.format(runtime_ast_copy))

    def rewrite_ast(self, node: ast.AST):
        node = MacroTransform(self.activation, self.token).visit(node)
        ExprContextFixer().visit(node)
        return node
