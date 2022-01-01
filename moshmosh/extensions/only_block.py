from moshmosh.extension import Extension
from moshmosh.ast_compat import ast

import itertools


class Only(Extension):
    identifier = "only-block"
    def __init__(self):
        self.visitor = OnlyTransformer(self.activation)
        # will it get reused? is stateful (only_defs)

    def rewrite_ast(self, node):
        node = self.visitor.visit(node)
        node.body = self.visitor.only_defs + node.body
        return node


class OnlyTransformer(ast.NodeTransformer):
    def __init__(self, activation):
        self.activation = activation
        self.only_defs = []
        self.ids = itertools.count()

    def visit_With(self, node):
        if (
            node.lineno in self.activation
            and len(node.items) == 1
            and (context := node.items[0].context_expr)
            and isinstance(context, ast.Call)
            and isinstance(context.func, ast.Name)
            and context.func.id == 'only'
        ):
            return self.desugar_only(node)
        else:
            return node

    def desugar_only(self, with_node):
        # print(ast.dump(with_node, indent=2))

        call = with_node.items[0].context_expr
        assert len(call.keywords) == 0, 'Not yet supported for only(): only(x=y) for arg renaming'
        assert all(isinstance(arg, ast.Name) for arg in call.args), 'Invalid syntax for only(): Bare expression not allowed as parameter'

        name = f'_only_block_{next(self.ids)}'
        call.func.id = name

        args = [ast.arg(arg=arg.id) for arg in call.args]
        for arg in args:
            ast.copy_location(arg, with_node)

        definition = ast.FunctionDef(
            name=name,
            args=ast.arguments(
                posonlyargs=[],
                args=args,
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=with_node.body,
            decorator_list=[],
            lineno=99999, # TODO
            col_offset=99999,  # TODO
        )
        self.only_defs.append(definition)

        # self.only_defs.append(ast.Expr(ast.Constant(value=1)))


        if with_node.items[0].optional_vars:  # with ... as ...:
            optional_vars = with_node.items[0].optional_vars
            assert isinstance(optional_vars, ast.Name), 'Not yet supported for only(): Destructuring assignment'
            target = with_node.items[0].optional_vars.id
            result = ast.Assign(
                targets=[
                    ast.Name(id=target, ctx=ast.Store())
                ],
                value=call
            )
            ast.copy_location(result, with_node)
            return result
        else:  # 'with' without 'as'
            # return ast.Expr(value=call)
            result = ast.Expr(value=call)
            ast.copy_location(result, with_node)
            return result
