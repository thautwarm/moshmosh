from moshmosh.extension import Extension
from moshmosh.ast_compat import ast


class PipelineVisitor(ast.NodeTransformer):
    """
    `a | f -> f(a)`, recursively
    """
    def __init__(self, activation):
        self.activation = activation

    def visit_BinOp(self, n: ast.BinOp):
        if n.lineno in self.activation and isinstance(n.op, ast.BitOr):
            return ast.Call(
                self.visit(n.right),
                [self.visit(n.left)],
                [],
                lineno=n.lineno,
                col_offset=n.col_offset
            )
        return self.generic_visit(n)

class Pipeline(Extension):
    identifier = "pipeline"
    def __init__(self):
        self.visitor = PipelineVisitor(self.activation)

    def rewrite_ast(self, node):
        return self.visitor.visit(node)
