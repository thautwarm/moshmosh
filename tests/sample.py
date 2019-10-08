# -*- coding: extension -*-
# +template-python

@quote
def f(x):
    x = x, y
    return x


import ast
from astpretty import pprint
suite = f(ast.Name("aks", ast.Load()))
node = ast.Module(suite)
ast.fix_missing_locations(node)
from astpretty import pprint
pprint(node)
