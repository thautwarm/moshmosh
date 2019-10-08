# -*- coding: extension -*-
# +pattern-matching
class MatchError(Exception):
    pass

with match(1):
    if case[0]:
        print(2)
    if case[a]:
        print(a + 2)

