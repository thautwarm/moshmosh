# Moshmosh

![example.png](https://raw.githubusercontent.com/thautwarm/moshmosh/master/example.png)

The TRUE implementation of pattern matching for Python.

For more than pattern matching, check `syntax_rule.py`.

```python
@syntax_rule(pattern_matching)
def f(x, r=1):
    with match(x):
        if case[0]: return 1
        if case[x]: return f(x-1, r * x)

return f(10)
```

# Features

- [x] Tree pattern matching: `if C1(C2(1), ""): ...`

- [x] Unlike projects using `inspect.getsource`, syntax extensions are achieved without evil IO operations or requiring source files.

- [x] Literal patterns:
    - [x] string, number and other constant patterns
    - [x] tuple, list patterns

- [x] Provided with the capabilities to customize semantics of python syntaxes.