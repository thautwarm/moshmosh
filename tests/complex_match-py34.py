from moshmosh.extensions.pattern_matching import *
class MatchError(Exception):
    pass

class C:
    @classmethod
    def __match__(cls, x, i):
        if i is not 2:
            raise MatchError
        return x, x

@syntax_rule(pattern_matching)
def f1(x):
    with match(x):
        if case[C(C(a, b), C(c, d))]: return (a, b, c, d)

assert f1(1) == (1, ) * 4

@syntax_rule(pattern_matching)
def f2(x, r=1):
    with match(x):
        if case[0]: return r
        if case[x]: return f2(x-1, r * x)

assert f2(5) == 120


@syntax_rule(pattern_matching)
def f3(x):
    with match(x):
        if case[[1, x]]:
            print(x)
            return sum(x)
        if case[(1, x, y)]: return x + y
        if case[_]: return 0

# assert f3([1, 2, 3, 4]) == 9

assert f3((1, 2, 3)) == 5
assert f3((1, 2, 3, 4)) == 0
assert f3(1) == 0