# Moshmosh

**Attention!!**: this project is not ready for practical use, because it just provides poor error reporting.

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

Installation: `pip install moshmosh-syntax`.


# Features

- [x] Tree pattern matching: `if case[C1(C2(1), "")]: ...`

- [x] Unlike projects using `inspect.getsource`, syntax extensions are achieved without evil IO operations or requiring source files.

- [x] Literal patterns:
    - [x] string, number and other constant patterns
    - [x] tuple, list patterns

- [x] Provided with the capabilities to customize semantics of python syntaxes.

# Benchmarks

Check benchmark.py.

Although Pampy is much weaker than moshmosh, it's also much slower than moshmosh :) .
Note tha moshmosh is currently a simple prototype implemented in few hours.

Thus we can safely conclude, **A true one is always better than the fakers**.

## Acknowledgements

See [older implementations](http://www.grantjenks.com/docs/patternmatching/#alternative-packages) and search "pattern matching" in [Python-ideas](https://mail.python.org/archives/list/python-ideas@python.org/).

Salute all the people used to work for Python pattern matching.