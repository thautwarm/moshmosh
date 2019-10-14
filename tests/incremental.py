from moshmosh.repl_apis import *

ext_builder = {}

src = perform_extension_incr(ext_builder, """
# +pattern-matching

with match(1):
    if 1: res = 114


# -pattern-matching
# +pipeline
""", "yoyoyo")

scope = {'__file__': __file__}
exec(src, scope)
assert scope['res'] == 114

src = perform_extension_incr(ext_builder, """
with match(1):
    if 1: res = 114
""", "yoyoyo")

res = None
try:
    exec(src, scope)
except NameError as e:
    res = e.args[0]

assert "name 'match' is not defined" == res



src = perform_extension_incr(ext_builder, """
[1] | print
""", "yoyoyo")

res = None
exec(src, scope)