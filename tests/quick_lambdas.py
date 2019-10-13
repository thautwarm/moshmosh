# moshmosh?
# +quick-lambda
# +pipeline
from tests.py35_unparse import Unparser
Unparser(__ast__)
from functools import reduce
print()
print()
x = map(_ + 1, _0_)
assert isinstance(x([1, 2, 3]), map)

x = [1, 2, 3] | map(_ + 1, _0_) | list
assert x == [2, 3, 4]

x = [3, 4, 5] | map(_ % 3, _0_) | list
assert x == [0, 1, 2]

assert reduce(_0 + _1, [10, 41, 59]) == 110

assert map(_1_, _0_)([1, 4, 3], _ + 2) | list == [3, 6, 5]
