import ast


def ast_to_literal(node):
    """
    Convert an AST to a python literal.
    We avoid the use of comprehension expressions here
    to get more human-friendly call stacks.
    """
    if isinstance(node, ast.AST):
        field_names = node._fields
        res = {'constructor': node.__class__.__name__}
        for field_name in field_names:
            field = getattr(node, field_name, None)
            field = ast_to_literal(field)
            res[field_name] = field
        if hasattr(node, 'lineno'):
            res['lineno'] = node.lineno
        if hasattr(node, 'col_offset'):
            res['col_offset'] = node.col_offset

        return res
    if isinstance(node, list):
        res = []
        for each in node:
            res.append(ast_to_literal(each))
        return res
    return node

def ast_to_literal_without_locations(node):
    if isinstance(node, ast.AST):
        field_names = node._fields
        res = {'constructor': node.__class__.__name__}
        for field_name in field_names:
            field = getattr(node, field_name, None)
            field = ast_to_literal_without_locations(field)
            res[field_name] = field

        return res
    if isinstance(node, list):
        res = []
        for each in node:
            res.append(ast_to_literal_without_locations(each))
        return res
    return node

def literal_to_ast(literal):
    """
    Convert a python literal to an AST.
    """
    if isinstance(literal, dict):
        ctor = literal.pop('constructor')
        ctor = getattr(ast, ctor)

        return ctor(**{k: literal_to_ast(v) for k, v in literal.items()})

    if isinstance(literal, list):
        return list(map(literal_to_ast, literal))

    return literal
