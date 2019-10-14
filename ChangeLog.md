Unreleased Notes
-----------------

2019/07/13:
commit: "compat Python3.x"

2019/10/08
- removed the use of uncompyle, instead, we introduced the mechanism from future-fstrings

2019/10/11
- removed the mechanism from future-fstrings due to the redundant manipulations, use Python import mechanism since then.
- more extensions:
    - `quick-lambdas`
    - `scoped-operators`
    - `pipelines`

2019/10/13:
- removed locations in quotations.
- added unpacking support for list and tuple patterns.


Released Notes
-----------------

2019/10/13:
- First released version: 0.2, supporting 3.5+

2019/10/14: adding the `lazy-import` extension.