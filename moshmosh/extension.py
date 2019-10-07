from rbnf.py_tools.unparse import Unparser
from io import StringIO
import ast


class PIP(ast.NodeTransformer):
    def visit_Name(self, name: ast.Name):
        if name.id == 'PIP':
            return ast.Constant(114514)
        return name


def unparse(node: ast.AST):
    io = StringIO()
    Unparser(node, file=io)
    return io.getvalue()


def extension(source_code):
    # FIXME: Haskell-like syntax extension system
    node = ast.parse(source_code)
    node = PIP().visit(node)
    source_code = unparse(node)
    return "print('114514')\n" + source_code
