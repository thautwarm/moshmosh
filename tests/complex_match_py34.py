from moshmosh.extensions.pattern_matching import *
class MatchError(Exception):
    pass

class C:
    @classmethod
    def __match__(cls, i, x):
        if i is not 2:
            return None
        return x, x

def f1(x):
    with match(x):
        if C(C(a, b), C(c, d)): return (a, b, c, d)

assert f1(1) == (1, ) * 4

def f2(x, r=1):
    with match(x):
        if 0: return r
        if x: return f2(x-1, r * x)

assert f2(5) == 120

def f3(x):
    with match(x):
        if [1, x]:
            print(x)
            return sum(x)
        if (1, x, y): return x + y
        if _: return 0

assert f3([1, 2, 3, 4]) == 9

assert f3((1, 2, 3)) == 5
assert f3((1, 2, 3, 4)) == 0
assert f3(1) == 0

with match(2, 1):
    if (a, b, c) or [a, b, c]:
        res = (a + b + c)
    if (hd, tl):
        res = (hd, tl)

assert res == (2, 1)
