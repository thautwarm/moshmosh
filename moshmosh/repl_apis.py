from moshmosh.extension import *
from moshmosh.extension import _extension_pragma_re_u

def update_pragmas(extension_builder: t.Dict[object, Extension], lines):
    """
    Traverse the source codes and extract out the scope of
    every extension. Incrementally.
    """
    # bind to local for faster visiting in the loop
    extension_pragma_re = _extension_pragma_re_u
    registered = Registered.extensions

    # for new cells of IPython, refresh the scoping info
    # of the extensions
    for ext in extension_builder.values():
        intervals = ext.activation.intervals
        if intervals:
            last = intervals.pop()
            intervals.clear()
            if type(last) is int:
                intervals.append(0)

    for i, line in enumerate(lines):
        pragma = extension_pragma_re.match(line)
        if pragma:
            pragma = pragma.groupdict()
            action = pragma['action']
            extension = pragma['ext']
            params = pragma['params'] or ''
            params = (param.strip() for param in params.split(','))
            params = tuple(i for i in params if i)
            try:
                ext_cls = registered[extension]
            except KeyError:
                # TODO: add source code position info
                raise ExtensionNotFoundError(extension)
            key = (ext_cls, params)

            ext = extension_builder.get(key, None)
            if ext is None:
                try:
                    ext = extension_builder[key] = ext_cls(*params)
                except Exception as e:
                    raise

            lineno = i + 1
            if action == "+":
                ext.activation.enable(lineno)
            else:
                ext.activation.disable(lineno)

    return list(extension_builder.values())

def perform_extension_incr(
    extension_builder: t.Dict[object, Extension],
    source_code,
    filename
):

    str_type = type(source_code)

    node = ast.parse(source_code, filename)
    if str_type is bytes:
        source_code = source_code.decode('utf8')

    extensions = update_pragmas(extension_builder, StringIO(source_code))
    extensions = sum(map(list, solve_deps(extensions)), [])

    string_io = StringIO()
    for each in extensions:
        each.pre_rewrite_src(string_io)

    for each in extensions:
        node = each.rewrite_ast(node)
        ast.fix_missing_locations(node)

    literal = ast_to_literal(node)
    string_io.write("import ast as _ast\n")
    string_io.write("from moshmosh.rewrite_helper import literal_to_ast as _literal_to_ast\n")
    string_io.write('\n')
    string_io.write('__literal__ = ')
    string_io.write(repr(literal))
    string_io.write('\n')
    string_io.write("__ast__ = _literal_to_ast(__literal__)\n")

    string_io.write('__code__ = compile')
    string_io.write('(__ast__, ')
    string_io.write('__import__("os").path.abspath("") if __name__ == "__main__" else __file__,')
    string_io.write('"exec")\n')

    string_io.write('exec(__code__, globals())\n')

    for each in extensions:
        each.post_rewrite_src(string_io)

    code = string_io.getvalue()
    if str_type is bytes:
        code = bytes(code, encoding='utf8')
    return code


class IPythonSupport:
    def __init__(self, builder: t.Dict[object, Extension]):
        self.builder = builder
        self.tmp_exts = None

    def input_transform(self, lines):
        self.tmp_exts = update_pragmas(self.builder, lines)
        return lines

    def ast_transform(self, node):
        extensions = self.tmp_exts
        extensions = sum(map(list, solve_deps(extensions)), [])

        prev_io = StringIO()
        for each in extensions:
            each.pre_rewrite_src(prev_io)

        prev_io.write("import ast as _ast\n")
        prev_io.write("from moshmosh.rewrite_helper import literal_to_ast as _literal_to_ast\n")
        prev_stmts = ast.parse(prev_io.getvalue()).body

        for each in extensions:
            node = each.rewrite_ast(node)
            ast.fix_missing_locations(node)

        post_io = StringIO()
        for each in extensions:
            each.post_rewrite_src(post_io)

        post_stmts = ast.parse(post_io.getvalue()).body
        node.body = prev_stmts + node.body + post_stmts
        return node
