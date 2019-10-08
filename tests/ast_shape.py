from astpretty import pprint
from ast import parse

import ast
print_ast = ast.Name("print", ast.Load())


pprint(parse("""

try:
    a
except Ex as e:
    print(e)
    
"""))
