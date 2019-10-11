from moshmosh.extension import perform_extension
from inspect import getsource
from pampy import match, _


def rewrite_fn(f, extensions=()):
    src = getsource(f)
    src = perform_extension(src)
    exec(src, f.__globals__)
    return f.__globals__[f.__name__]


def test_pampy(data):
    for datum in data:
        match(datum, [_, str, _], lambda a, b, c: "%s(%s)%s" % (a, b, c),
              (str, int), lambda a, b: a * b, (int, int), lambda a, b: "%d%d" %
              (a, b))


class TypeMatcher:
    def __init__(self, t):
        def match(i, x):
            if i is not 1 or not isinstance(x, t):
                return None
            return x,

        self.__match__ = match


Str = TypeMatcher(str)
Int = TypeMatcher(int)


def test_mm(data):
# +pattern-matching
    for d in data:
        with match(d):
            if [a, Str(b), c]:
                "%s(%s)%s" % (a, b, c)
            if (Str(s), Int(i)):
                s * i
            if (Int(i1), Int(i2)):
                "%d%d" % (i1, i2)


rewrite_fn(test_mm)

data = [("xx", 3), ("yyy", 2), (1, 2), (5, 6), (1000, 2000)]

test_pampy(data)
test_mm(data)



# %timeit test_mm(data)
# 6.76 µs ± 239 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

# %timeit test_pampy(data)
# 59.9 µs ± 797 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
