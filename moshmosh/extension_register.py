import sys
from moshmosh.extension import perform_extension, check_if_use_moshmosh_sys
from importlib._bootstrap import ModuleSpec
from importlib._bootstrap_external import (PathFinder, FileLoader,
                                           SourceFileLoader,
                                           SourcelessFileLoader,
                                           ExtensionFileLoader)

__all__ = []


class ProxySourceFileLoader(SourceFileLoader):
    def __init__(self, loader: SourceFileLoader):
        SourceFileLoader.__init__(self, loader.name, loader.path)

    def get_data(self, path: str):
        data = SourceFileLoader.get_data(self, path)
        if check_if_use_moshmosh_sys(data):
            return perform_extension(data, self.path)
        return data


class ProxySourcelessLoader(SourcelessFileLoader):
    def __init__(self, loader: SourcelessFileLoader):
        SourcelessFileLoader.__init__(self, loader.name, loader.path)

    def get_data(self, path: str):
        data = SourcelessFileLoader.get_data(self, path)
        if check_if_use_moshmosh_sys(data):
            return perform_extension(data, self.path)
        return data


class MoshmoshFinder(PathFinder):
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)
        if spec and spec.loader and isinstance(spec.loader, FileLoader):
            loader = spec.loader
            loader_ty = loader.__class__
            loader_ = {
                SourcelessFileLoader: lambda: ProxySourcelessLoader(loader),
                SourceFileLoader: lambda: ProxySourceFileLoader(loader),
                ExtensionFileLoader: lambda: loader
            }[loader_ty]()
            spec.loader = loader_
        return spec


sys.meta_path.insert(0, MoshmoshFinder)
