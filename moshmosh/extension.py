import ast
from io import StringIO
from moshmosh.rewrite_helper import ast_to_literal


class PIP(ast.NodeTransformer):
    """
    demo transformer
    """
    def visit_Name(self, name: ast.Name):
        if name.id == 'PIP':
            return ast.Constant(114514, lineno=name.lineno, col_offset=name.col_offset)
        return name


def extension(source_code):
    # FIXME: Haskell-like syntax extension system
    node = ast.parse(source_code)
    node = PIP().visit(node)
    literal = ast_to_literal(node)
    string_io = StringIO()
    string_io.write("""
import ast as _ast
def _literal_to_ast(literal):
    '''
    Convert a python literal to an AST.
    '''
    if isinstance(literal, dict):
        ctor = literal.pop('constructor')
        ctor = getattr(_ast, ctor)
        return ctor(**{k: _literal_to_ast(v) for k, v in literal.items()})

    if isinstance(literal, list):
        return list(map(_literal_to_ast, literal))

    return literal

    """)
    string_io.write('\n')
    string_io.write('__literal__ = ')
    string_io.write(repr(literal))
    string_io.write('\n')
    string_io.write('__ast__ = _literal_to_ast(__literal__)\n')
    # string_io.write('from astpretty import pprint;pprint(__ast__)\n')
    string_io.write('__code__ = compile(__ast__, __file__, "exec")\n')
    string_io.write('exec(__code__, globals())\n')
    code = string_io.getvalue()
    return code
