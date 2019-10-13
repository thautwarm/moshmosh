from moshmosh.extension import Extension
from moshmosh.ast_compat import ast
import re

class LambdaCollector(ast.NodeTransformer):
    def __init__(self, pattern: 're.Pattern', mk_arg): # re.Pattern might not found
        self.mk_arg = mk_arg
        self.pattern = pattern
        self.max_arg_index = -1

    def found_quick_lambda(self):
        return self.max_arg_index is not -1

    def visit_Name(self, n: ast.Name):
        match = self.pattern.match(n.id)
        if match:
            ith = match.group('ith')
            if ith:
                ith = int(ith)
                self.max_arg_index = max(self.max_arg_index, ith)
                n.id = '.' + n.id
            else:
                self.max_arg_index = max(0, self.max_arg_index)
                n.id = '.' + self.mk_arg(0)

        return n

class CollectorDelegate:
    def __init__(self, cls, token, mk_arg):
        pattern = re.compile(mk_arg("(?P<ith>\d*)") + '$')
        self.collector = cls(pattern, mk_arg)
        self._mk_new = lambda : cls(pattern, mk_arg)

    def mk_new_(self):
        self.collector = self._mk_new()

    def get(self):
        return self.collector

class QuickLambdaDetector(ast.NodeTransformer):
    """
    scala-style lambdas, not recursively processed.
    """
    def __init__(self, activation, token: str):
        self.arg_col = CollectorDelegate(
            LambdaCollector,
            token,
            lambda x: "{}{}".format(token, x)
        )

        self.placeholder_col = CollectorDelegate(
            LambdaCollector,
            token,
            lambda x: "{}{}_".format(token, x)
        )
        self.activation = activation

    def visit_Call(self, call: ast.Call):
        if call.lineno in self.activation:
            def mk_quick_lam(col: CollectorDelegate, arg: ast.AST):
                if arg.lineno in self.activation:
                    assert not isinstance(arg, ast.Starred)
                    cur_collector = col.get()
                    arg = cur_collector.visit(arg)
                    if cur_collector.found_quick_lambda():
                        col.mk_new_()
                        argcount = cur_collector.max_arg_index + 1
                        return ast.Lambda(
                            ast.arguments(
                                [
                                    ast.arg(
                                        '.' + cur_collector.mk_arg(i),
                                        annotation=None
                                    )
                                    for i in range(argcount)
                                ],
                                vararg=None,
                                kwonlyargs=[],
                                kw_defaults=[],
                                kwarg=None,
                                defaults=[]
                            ),
                            arg
                        )
                return arg
            call.func = self.visit(call.func)
            call.args = [mk_quick_lam(self.arg_col, arg) for arg in call.args]
            call.keywords = [mk_quick_lam(self.arg_col, arg) for arg in call.keywords]
            return mk_quick_lam(self.placeholder_col, call)
        return  self.generic_visit(call)
class QuickLambda(Extension):
    identifier = "quick-lambda"
    def __init__(self, token: str=None):
        token = token or '_'
        self.detector = QuickLambdaDetector(self.activation, token)

    def rewrite_ast(self, node):
        node = self.detector.visit(node)
        # from rbnf_rts.unparse import Unparser
        # Unparser(node)
        return node
