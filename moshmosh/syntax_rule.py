from __future__ import print_function

from .ast_compat import ast
from uncompyle6 import code_deparse
from io import StringIO
from inspect import signature as get_signature, _empty as empty
from types import FunctionType
from textwrap import indent
from time import time


try:
    from rbnf.py_tools.unparse import Unparser as print_ast
except ImportError:
    try:
        from astpretty import pprint as print_ast
    except ImportError:
        print_ast = print

try:
    from typing import *
except:
    pass


class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

def syntax_rule(transformer, debug=False):
    return lambda f: _syntax_rule(f, transformer, debug)

def _syntax_rule(f, transformer, debug):
    mangle = str(time()).replace(".", "_")

    assert isinstance(f, FunctionType)
    sio = StringIO()

    code_deparse(f.__code__, out=sio)
    func_body_codestr = sio.getvalue()

    # `func_body_codestr` has no info of function head,
    # thus we should get the header manually.
    signature = get_signature(f)

    # for Python 3.6-, we should get the
    # correct order of function parameters.
    varnames = f.__code__.co_varnames
    params = sorted(signature.parameters.items(),
                    key=lambda pair: varnames.index(pair[0]))

    # Now, note that not all default value of a parameter
    # can be represented(via `repr`) directly. Say,
    #
    # ```
    # class S: pass
    # def f(a=S()):
    #   pass
    # ```
    #
    # in above codes you just cannot deparse the code object
    # into source code like
    #   `def f(a=<__main__.S object at 0x7f8c8c1692e8>): ...
    #
    # Also similar issues get raised up if any free variable here.
    #
    # As a result, please check my following codes for resolutions.

    freevars = {}
    for (name, param) in params:
        can_have_objects = ("default", "annotation")
        for obj_name in can_have_objects:
            obj = getattr(param, obj_name)
            if obj is not empty:
                # mangling here
                var_name = "_%s_%d" % (mangle, len(freevars))
                freevars[var_name] = obj
                setattr(param, "_" + obj_name, Var(var_name))

    for name, freevar in zip(f.__code__.co_freevars, f.__closure__ or ()):
        freevars[name] = freevar.cell_contents

    # the function header
    header = "def {name}{sig}:".format(name=f.__name__, sig=str(signature))
    func_def_codestr = header + "\n" + indent(func_body_codestr, prefix=" "*2)

    fn_ast = ast.parse(func_def_codestr).body[0]
    if debug:
        print_ast(fn_ast)

    # perform your transformation on the function's AST.
    fn_ast = transformer(fn_ast)

    # debug
    if debug:
        ast.fix_missing_locations(fn_ast)
        print_ast(fn_ast)

    # Now we have all code piece for the function definition, but we
    # should handle the closures/default args.
    freevars = list(freevars.items())

    ast_for_all = ast.FunctionDef(
        # also mangling here
        name=".closure_func",
        args=ast.arguments(
            args=[ast.arg(arg=freevar_name, annotation=None) for (freevar_name, _) in freevars],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
            ),
        body=[fn_ast, ast.Return(ast.Name(f.__name__, ctx=ast.Load()))],
        decorator_list=[],
        returns=None,
        )
    ast.fix_missing_locations(ast_for_all)

    code = compile(ast.Module([ast_for_all]), f.__code__.co_filename, "exec")

    exec(code, f.__globals__)
    closure_func = f.__globals__['.closure_func']
    del f.__globals__['.closure_func']
    return closure_func(*[var for (_, var) in freevars])

if __name__ == '__main__':

    @syntax_rule(lambda x: x)
    def f(x, y=1, **kw):
        return x + y
