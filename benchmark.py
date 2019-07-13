from pampy import match, _
from pattern_matching import *


def test_pampy(data):
    for datum in data:
        match(datum,
            [_, str, _], lambda a, b, c: "%s(%s)%s"%(a, b, c),
            (str, int), lambda a, b: a * b,
            (int, int), lambda a, b: "%d%d"%(a, b))

class MatchError(Exception):
    pass

class TypeMatcher:
    def __init__(self, t):
        def match(x, i):
            if i is not 1 or not isinstance(x, t):
                raise MatchError
            return (x, )
        self.__match__ = match

Str = TypeMatcher(str)
Int = TypeMatcher(int)

@syntax_rule(pattern_matching)

def test_mm(data):
    for d in data:
        with match(d):
            if case[[a, Str(b), c]]:
                "%s(%s)%s"%(a, b, c)
            if case[(Str(s), Int(i))]:
                s * i
            if case[(Int(i1), Int(i2))]:
                "%d%d"%(i1, i2)

data = [("xx", 3), ("yyy", 2), (1, 2), (5, 6), (1000, 2000)]

test_pampy(data)
test_mm(data)

# %timeit test_mm(data)
# 9.83 µs ± 85.9 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

# %timeit test_pampy(data)
# 52.8 µs ± 797 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)