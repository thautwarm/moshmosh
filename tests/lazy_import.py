# moshmosh?

from moshmosh.extensions.lazy_import import LazyModule
# +lazy-import
import io

assert issubclass(type(io), LazyModule)
assert isinstance(io, LazyModule)

repr(io)

assert not issubclass(type(io), LazyModule)
assert not isinstance(io, LazyModule)
# -lazy-import
import subprocess
assert not issubclass(type(subprocess), LazyModule)
assert not isinstance(subprocess, LazyModule)
