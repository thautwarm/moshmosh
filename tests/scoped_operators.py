# moshmosh?
# +scoped-operator(+, myadd)


def myadd(a, b):
    return (a, b)

assert (1 + 5) == (1, 5)

# -scoped-operator(+, myadd)
assert (1 + 5) == 6
