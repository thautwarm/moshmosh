# moshmosh?

# +pipeline
assert "pipeline enabled" | len == len("pipeline enabled")
# -pipeline
_ = 1 | 2

# +pipeline
assert [1, 2, 3] | (lambda x: map(lambda x: x + 1, x)) | list == [2, 3, 4]