from astpretty import pprint
from ast import parse
# from moshmosh.extensions import pattern_matching
import ast
print_ast = ast.Name("print", ast.Load())


pprint(parse("""
from a import b
from . import c
import b
from . import *
"""))
