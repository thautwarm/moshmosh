from moshmosh.extension import *
def update_pragmas(lines):
    """
    Traverse the source codes and extract out the scope of
    every extension.
    """
    # bind to local for faster visiting in the loop
    extension_pragma_re = _extension_pragma_re_u
    registered = Registered.extensions
    # allow manually setting enable order
    extension_builder = OrderedDict()  # type: t.Dict[object, Extension]

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

def perform_extension_incr(source_code, exts, filename):

    str_type = type(source_code)

    node = ast.parse(source_code, filename)
    if str_type is bytes:
        source_code = source_code.decode('utf8')

    extensions = extract_pragmas(StringIO(source_code))

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
    string_io.write('__code__ = compile(__ast__, __file__, "exec")\n')
    string_io.write('exec(__code__, globals())\n')

    for each in extensions:
        each.post_rewrite_src(string_io)

    code = string_io.getvalue()
    if str_type is bytes:
        code = bytes(code, encoding='utf8')
    return code
