from moshmosh.extension import Extension
from moshmosh.ast_compat import ast

# https://github.com/python/cpython/blob/master/Parser/Python.asdl#L102
opname_map = {
    "+": 'Add',
    '-': 'Sub',
    '*': 'Mult',
    '/': 'Div',
    '%': 'Mod',
    '**': 'Pow',
    '<<': 'LShift',
    '>>': 'RShift',
    '|': 'BitOr',
    '^': 'BitXor',
    '&': 'BitAnd',
    '//': 'FloorDiv'
}


class ScopedOperatorVisitor(ast.NodeTransformer):
    """
    `a op b -> func(a, b)`, recursively.
    The `op => func` pair is specified by users.
    """
    def __init__(self, activation, op_name: str, func_name: str):
        self.pair = (op_name, func_name)
        self.activation = activation

    def visit_BinOp(self, n: ast.BinOp):
        if n.lineno in self.activation:
            name = n.op.__class__.__name__
            pair = self.pair
            if name == pair[0]:
                fn = ast.Name(pair[1], ast.Load())
                return ast.Call(
                    fn,
                    [self.visit(n.left), self.visit(n.right)],
                    [],
                    lineno=n.lineno,
                    col_offset=n.col_offset
                )

        return self.generic_visit(n)


class ScopedOperator(Extension):
    identifier = "scoped-operator"

    def __init__(self, op_name: str, func_name: str):
        self.op_name = opname_map.get(op_name, op_name)
        self.func_name = func_name
        self.visitor = ScopedOperatorVisitor(
            self.activation,
            self.op_name,
            self.func_name
        )

    def rewrite_ast(self, node):
        return self.visitor.visit(node)
