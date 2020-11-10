# moshmosh?
# +extend-dict

a = {1: 2, 3: 4, 'z': 10}
b = {5: 6, **a, 1: 10}

print(b)

assert b[5] == 6 and b[3] == 4 and b[1] == 10

b = {7: a, **b, **a}

assert b[7] is a and b[1] == 2

assert 10 == b_z

assert a == b_7