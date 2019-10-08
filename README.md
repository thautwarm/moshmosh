# Moshmosh

An advanced syntax extension system implemented in pure python.

# Extension Syntax

```python
# moshmosh?

# Use extension
# +<extension name>[<extension arg>{','}]

<do stuff with your extensions>

# Unset extension
# -<extension name>[<extension arg>{','}]
```

The first line of the file should start with a comment `# moshmosh?`, which tells us
that it's expected to use Moshmosh extension system.

## Case Study : Pattern Matching

```python
# moshmosh?
# +pattern-matching

with match(114, 514):
    if case[(a, b)]:
        print(a)

# => 114
```

## Case Study : Template-Python

```python
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

# =>
Expr(
    lineno=7,
    col_offset=4,
    value=BinOp(
        lineno=7,
        col_offset=4,
        left=Name(lineno=7, col_offset=4, id='a', ctx=Load()),
        op=Add(),
        right=Num(lineno=7, col_offset=8, n=1),
    ),
)
Assign(
    lineno=8,
    col_offset=4,
    targets=[Name(lineno=8, col_offset=4, id='a', ctx=Store())],
    value=BinOp(
        lineno=8,
        col_offset=8,
        left=Name(lineno=8, col_offset=8, id='y', ctx=Load()),
        op=Add(),
        right=Num(lineno=8, col_offset=12, n=1),
    ),
)
```

## Acknowledgements


- [future-fstrings](https://github.com/asottile/future-fstrings)
- Pattern matching in Python
    - [older implementations](http://www.grantjenks.com/docs/patternmatching/#alternative-packages)
    - search "pattern matching" at [Python-ideas](https://mail.python.org/archives/list/python-ideas@python.org/).
