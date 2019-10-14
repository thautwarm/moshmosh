# moshmosh?
# +pattern-matching

with match(1, 2):
    if (a, pin(3)):
        print(a)
    if (_, pin(2)) and (pin(1), _):
        print(10)
    if _:
        print(5)

with match([1, 2, 3, 4]):
    if [1, 2, a, b]:
        print(a + b)


class Succ:
    @classmethod
    def __match__(cls, n, tag):
        if n == 0 or not isinstance(tag, int):
            return None  # failed

        return tuple(tag + 1 for i in range(n))


def f(val):
    with match(val):
        if (4, Succ(3, x, y, z)) or (3, Succ(4, x, y, z)):
            print(x + y + z)
        if _:
            print('otherwise')


f((4, 2))
f((3, 3))


class GreaterThan:
    def __init__(self, v):
        self.v = v

    def __match__(self, cnt: int, to_match):
        if isinstance(to_match, int) and cnt is 0 and to_match > self.v:
            return ()  # matched


with match(114, 514):
    if (GreaterThan(42)() and a, b):
        print(b, a)
