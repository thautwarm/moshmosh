import moshmosh
import sys
from importlib import import_module
from wisepy2 import wise


def runtests():
    from tests.test_all import Test
    Test().test_extensions()

@wise
def cli(*, test: bool = False, file=''):
    if test:
        runtests()
    if file:
        import_module("tests." + file)

if __name__ == '__main__':
    cli(sys.argv[1:])