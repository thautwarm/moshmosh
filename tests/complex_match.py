# moshmosh?
# +pattern-matching
# +quick-lambda
# +pipeline

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
# +pattern-matching
    with match(x):
        if [1, *x]:
            print(x)
            return sum(x)
        if (1, x, y): return x + y
        if _: return 0


assert f3([1, 2, 3, 4]) == 9
assert f3((1, 2, 3)) == 5
assert f3((1, 2, 3, 4)) == 0
assert f3(1) == 0

with match([4, 2, 3]):
    if [hd, *tl]:
        res = map(_ + hd, tl) | list

assert res == [6, 7]

with match(2, 1, 2, 3):
    if (a, b, c) or [a, b, c]:
        res = (a + b + c)
    if (hd, *tl):
        res = (hd, tl)

assert res == (2, (1, 2, 3))


def test_fn(data):
    with match(data):
        if (e, isinstance(int) and count):
            res =  [e] * count
        if (a, b, _) or [_, a, b]:
            res = (a + b)
        if (hd, *tl) or [hd, *tl]:
            res = (hd, tl)
        if "42":
            res = 42
    return res

assert test_fn([1, 2, 3]) == 5
assert test_fn((1, 2, 3)) == 3
assert test_fn((1, 2)) == [1, 1]
assert test_fn((object, 3)) == [object, object, object]
assert test_fn((object, 3, 4, 5)) == (object, (3, 4, 5))
assert test_fn("42") == 42
from moshmosh.extensions.pattern_matching import NotExhaustive

try:
    test_fn(1)
except NotExhaustive:
    pass