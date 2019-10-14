# moshmosh?
# +template-python
from moshmosh.extension import Extension
from moshmosh.ast_compat import ast
from moshmosh.extensions.lazy_import.runtime import LazyModule

runtime_lazy_mod = "_moshmosh_lazy_module"


class LazyImportVisitor(ast.NodeTransformer):
    def __init__(self, act):
        self.act = act

    def visit_Import(self, imp: ast.Import):
        if imp.lineno not in self.act:
            return imp

        @quote
        def f(lazy_module, name, asname, names_var):
            for name, asname, in names_var:
                lazy_module(globals(), name, asname)

        names_var = ast.Constant(tuple((name.name, name.asname) for name in imp.names))
        name = ast.Name(".name")
        asname = ast.Name(".asname")
        return f(ast.Name(runtime_lazy_mod, ast.Load()), name, asname, names_var)

    def visit_ImportFrom(self, imp: ast.ImportFrom):
        if imp.lineno not in self.act or imp.names[0].name == '*':
            return imp
        if imp.module is None:
            from_mod = ast.Name(".from_mod")
            @quote
            def mk_from_mod(from_mod_n, level):
                from_mod_n = '.'.join(__name__.split('.')[:-level])
            mk_from_mod = mk_from_mod(from_mod, ast.Constant(imp.level))
        else:
            mk_from_mod = []
            from_mod = ast.Constant(imp.module)

        names_var = ast.Constant(tuple((name.name, name.asname) for name in imp.names))
        name = ast.Name(".name")
        asname = ast.Name(".asname")
        @quote
        def f(lazy_module, from_mod, name, asname, names_var):
            for name, asname, in names_var:
                lazy_module(globals(), name, asname, from_mod)
        stmts = f(
            ast.Name(runtime_lazy_mod, ast.Load()),
            from_mod,
            name,
            asname,
            names_var
        )
        mk_from_mod.extend(stmts)
        return stmts


class LazyImport(Extension):
    identifier = "lazy-import"

    def __init__(self):
        self.visitor = LazyImportVisitor(self.activation)

    def rewrite_ast(self, node):
        node = ast.fix_missing_locations(self.visitor.visit(node))
        # from astpretty import pprint
        # pprint(node)
        return node

    def pre_rewrite_src(self, io):
        io.write("from {} import {} as {}\n".format(__name__, LazyModule.__name__, runtime_lazy_mod))
