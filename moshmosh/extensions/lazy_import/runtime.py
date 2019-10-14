from importlib import import_module
from types import ModuleType

def import_module_plus(name, from_mod=None, package=None):
    if from_mod is not None:
        mod = import_module(from_mod, package)
        try:
            return getattr(mod, name)
        except AttributeError:
            path = mod.__file__
            exc = ImportError()
            exc.msg = "Module {} cannot import {}".format(
                from_mod,
                name
            )
            exc.path = path
            exc.name = from_mod
            raise exc
    else:
        return import_module(name, package)

def import_and_replace(globals, name, asname, from_mod, package):
    mod = import_module_plus(name, from_mod, package)
    if asname:
        globals[asname] = mod
    else:
        globals[name] = mod
    return mod

class LazyModule(ModuleType):
    __imp_info__ = ()

    def __init__(self, globals, name, asname=None, from_mod=None, package=None):
        object.__setattr__(self, '__imp_info__', (globals, name, asname, from_mod, package))
        if asname:
            globals[asname] = self
        else:
            globals[name] = self

    def __getattr__(self, name):
        imp_info = object.__getattribute__(self, '__imp_info__')
        mod = import_and_replace(*imp_info)
        return getattr(mod, name)

    def __delattr__(self, name):
        imp_info = object.__getattribute__(self, '__imp_info__')
        mod = import_and_replace(*imp_info)
        return delattr(mod, name)

    def __setattr__(self, name, value):
        imp_info = object.__getattribute__(self, '__imp_info__')
        mod = import_and_replace(*imp_info)
        return setattr(mod, name, value)
