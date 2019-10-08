from moshmosh.extensions.pattern_matching.runtime import ListView
v = ListView([1, 2, 3, 5], range(1, 4))
v.sort(reverse=True)
assert v == [5, 3, 2]

v.sort(reverse=False)
assert v == [2, 3, 5]

v.sort(reverse=False, key=lambda x: -x)

assert v == [5, 3, 2]

assert isinstance(v, list)