from pattern_matching import *
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
        if case[C(C(a, b), C(c, d))]: print(a, b, c, d)

f1(1)

@syntax_rule(pattern_matching)
def f2(x, r=1):
    with match(x):
        if case[0]: return r
        if case[x]: return f2(x-1, r * x)

print(f2(5))
