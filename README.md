# Moshmosh

[![Build](https://travis-ci.com/thautwarm/moshmosh.svg?branch=master)](https://travis-ci.com/thautwarm/moshmosh) [![Support](https://img.shields.io/badge/PyPI-&nbsp;3\.5~3\.7-Orange.svg?style=flat)](https://pypi.org/project/moshmosh-base) [![codecov](https://codecov.io/gh/thautwarm/moshmosh/branch/master/graph/badge.svg)](https://codecov.io/gh/thautwarm/moshmosh)

An advanced syntax extension system implemented in pure python.

```
pip install moshmosh-base
```

# Preview

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

class GreaterThan:
    def __init__(self, v):
        self.v = v

    def __match__(self, cnt: int, to_match):
        if isinstance(to_match, int) and cnt is 0 and to_match > self.v:
            return () # matched
        # 'return None' indicates 'unmatched'

with match(114, 514):
    if (GreaterThan(42)() and a, b):
        print(b, a)
```

The syntax of pattern matching:
```python

# +pattern-matching(token_name='match')

with <token_name>(value):
    if pat1:
        body1
    if pat2:
        body2
    ...
```

The matching should be exhaustive, otherwise,
a `moshmosh.extensions.pattern_matching.runtime.NotExhaustive`
might get raised.

Supported Patterns:
- And pattern: `pat1 and pat2 and pat3 ...`
- Or pattern: `pat1 or pat2 or pat3...`
- Pin pattern: `pin(value)`
- Literal pattern: `1, "str", 1+2j, (1, 2),`
- As pattern: `a, var`
- Wildcard: `_`
- Nested patterns:
    - Tuple: `(pat1, pat2, pat3), (pat1, *pat2, pat3)`
    - List:  `[pat1, pat2, pat3], [pat1, *pat2, pat3]`
    - Recogniser: `Cons(pat1, pat2, pat3)`, note that,
        the function `Cons.__match__(<n arg>, value_to_match)` is exact the protocol.



## Case Study : Template-Python

```python
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
