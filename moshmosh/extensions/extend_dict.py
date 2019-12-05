from moshmosh.extension import Extension
from moshmosh.ast_compat import ast


class ExtendDictVisitor(ast.NodeTransformer):

    def __init__(self, activation, token: str) -> None:
        super().__init__()
        self.activation = activation
        self.token = token

    def visit_Name(self, n: ast.Name):
        if n.lineno not in self.activation or len(n.id) < 3 or "_" not in n.id:
            return self.generic_visit(n)

        dict_name, key_name = n.id.split("_")

        if dict_name is None or key_name is None:
            return self.generic_visit(n)

        if key_name.isdigit():
            index_value = ast.Num(n=int(key_name))
        else:
            index_value = ast.Str(s=key_name)

        return ast.Subscript(
            value=ast.Name(id=dict_name, ctx=ast.Load()),
            slice=ast.Index(value=index_value),
            ctx=ast.Load(),
            lineno=n.lineno,
            col_offset=n.col_offset
        )


class ExtendDict(Extension):
    identifier = "extend-dict"

    def __init__(self, token: str = None) -> None:
        super().__init__()
        self.visitor = ExtendDictVisitor(activation=self.activation, token=token)

    def rewrite_ast(self, node):
        return self.visitor.visit(node)
