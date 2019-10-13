from moshmosh.extension import perform_extension
from inspect import getsource
from pampy import match, _


def rewrite_fn(f):
    src = getsource(f)
    src = perform_extension(src)
    exec(src, f.__globals__)
    return f.__globals__[f.__name__]

def test_pampy(data):
    for datum in data:
        match(datum, [_, str, _], lambda a, b, c: "%s(%s)%s" % (a, b, c),
              (str, int), lambda a, b: a * b, (int, int), lambda a, b: "%d%d" %
              (a, b))


def mk(_isinstance):
    def test_mm(data):
        isinstance = _isinstance
    # +pattern-matching
        for d in data:
            with match(d):
                if [a, isinstance(str) and b, c]:
                    "%s(%s)%s" % (a, b, c)
                if (isinstance(str) and s, isinstance(int) and i):
                    s * i
                if (isinstance(int) and i1, isinstance(int) and i2):
                    "%d%d" % (i1, i2)
    return test_mm

rewrite_fn(mk)

data = [("xx", 3), ("yyy", 2), (1, 2), (5, 6), (1000, 2000)]

test_mm = mk(isinstance)
test_pampy(data)
test_mm(data)

from timeit import timeit

time1 = timeit("test(data)", globals=dict(data=data, test=test_pampy), number=10000)
time2 = timeit("test(data)", globals=dict(data=data, test=test_mm), number=10000)
# In [1]: %timeit test_pampy(data)
# 56.6 µs ± 824 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

# In [2]: %timeit test_mm(data)
# 3.93 µs ± 86.5 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

assert time1 / time2 > 10
print("pampy : {}\nmoshmosh: {}\npampy/moshmosh: {}".format(time1, time2, time1/time2))
