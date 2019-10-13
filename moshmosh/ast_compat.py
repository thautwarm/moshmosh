import ast as _ast
from types import ModuleType
from sys import version_info

from numbers import Number


class SupertypeMeta(type):
    def __instancecheck__(self, other):
        return isinstance(other, self._sup_cls)


class ConsistentConstant(metaclass=SupertypeMeta):
    _sup_cls = (_ast.Num, _ast.NameConstant, _ast.Str)

    def __new__(self, i):
        if isinstance(i, Number):
            return ast.Num(i)
        if isinstance(i, str):
            return ast.Str(i)
        if isinstance(i, tuple) and version_info < (3, 6):
            return ast.Tuple(elts=list(map(ConsistentConstant, i)), ctx=ast.Load())
        return ast.NameConstant(i)

if version_info < (3, 7):
    ast = ModuleType("ast", _ast.__doc__)

    def make_new_init(supercls, fields_):
        def init(self, *args, **kwargs):
            supercls.__init__(self)
            fields = iter(fields_)
            for arg in args:
                field = next(fields)
                setattr(self, field, arg)
            for field in fields:
                v = kwargs.get(field)
                if v is not None:
                    setattr(self, field, v)

        return init

    for k, v in _ast.__dict__.items():
        if isinstance(v, type) and issubclass(v, _ast.AST):
            ns = {"__init__": make_new_init(v, v._fields), "_sup_cls": v}
            v = SupertypeMeta(k, (v, ), ns)

        setattr(ast, k, v)

    if not hasattr(_ast, "Constant"):

        class Constant(ConsistentConstant):
            pass

        ast.Constant = Constant
        def get_constant(n: Constant):
            if isinstance(n, ast.Num):
                return n.n
            elif isinstance(n, ast.Str):
                return n.s
            return n.value
    else:
        def get_constant(n: ast.Constant):
            return n.value

    if not hasattr(_ast, "Starred"):

        class Starred:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError

        ast.Starred = Starred

    if not hasattr(_ast, "AnnAssign"):

        class AnnAssign:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError

        ast.AnnAssign = AnnAssign
else:
    ast = _ast
    def get_constant(n: ast.Constant):
        return n.value