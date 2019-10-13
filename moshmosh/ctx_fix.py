from moshmosh.ast_compat import ast


class ExprContextWriter(ast.NodeVisitor):
    def __init__(self, ctx):
        self.ctx = ctx

    def _store_simply(self, node):
        node.ctx = self.ctx

    def _store_recursively(self, node):
        node.ctx = self.ctx
        self.generic_visit(node)

    visit_Name = _store_simply
    visit_Subscript = _store_simply
    visit_Attribute = _store_simply
    visit_Tuple = _store_recursively
    visit_List = _store_recursively
    visit_Starred = _store_recursively


_store_writer = ExprContextWriter(ast.Store())
_del_writer = ExprContextWriter(ast.Del())


class ExprContextFixer(ast.NodeVisitor):
    def visit_AnnAssign(self, n: ast.AnnAssign):
        _store_writer.visit(n.target)
        self.generic_visit(n.annotation)
        if n.value:
            self.generic_visit(n.value)

    def visit_AugAssign(self, n: ast.AugAssign):
        _store_writer.visit(n.target)
        self.generic_visit(n.value)

    def visit_Assign(self, n: ast.Assign):
        for target in n.targets:
            _store_writer.visit(target)
        self.generic_visit(n.value)

    def visit_Delete(self, n: ast.Delete):
        for target in n.targets:
            _del_writer.visit(target)

    def visit_Name(self, n: ast.Name):
        if not hasattr(n, 'ctx') or n.ctx is None:
            n.ctx = ast.Load()
