from pattern_matching import *

class MatchError(Exception):
    pass


class C:
    @classmethod
    def __match__(cls, x, i):
        if i is not 2:
            raise MatchError
        return x, x

@syntax_rule(PatternMatching().visit, debug=True)
def f1(x):
    with match(x):
        if C(C(a, b), C(c, d)): print(a, b, c, d)

f1(1)


@syntax_rule(pattern_matching, debug=True)
def f2(x, r=1):
    with match(x):
        if 0: return 1
        if x: return f2(x-1, r * x)

print(f2(10))
