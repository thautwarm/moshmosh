# moshmosh?
# +pattern-matching
from rbnf_rts.unparse import Unparser
Unparser(__ast__)
with match(2, 1, 2, 3):
    if (a, b, c) or [a, b, c]:
        print(a + b + c)
    if (hd, *tl):
        print(hd, tl)

