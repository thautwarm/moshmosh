# moshmosh?
# +template-python


@quote
def f(x):
    x + 1
    x = y + 1

import ast
from astpretty import pprint

stmts = f(ast.Name("a"))
pprint(stmts[0])
pprint(stmts[1])
