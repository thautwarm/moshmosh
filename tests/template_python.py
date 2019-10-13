# moshmosh?
# +template-python

@quote
def f(x):
    x + 1
    x = y + 1

from moshmosh.ast_compat import ast
from astpretty import pprint

stmts = f(ast.Name("a"))

pprint(ast.fix_missing_locations(stmts[0]))
pprint(ast.fix_missing_locations(stmts[1]))
