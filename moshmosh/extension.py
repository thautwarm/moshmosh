import abc
import typing as t
import re
from collections import OrderedDict
from io import StringIO
from moshmosh.rewrite_helper import ast_to_literal
from moshmosh.ast_compat import ast

_extension_token_b = re.compile(b"#\s*moshmosh\?\s*?")
_extension_token_u = re.compile(r"#\s*moshmosh\?\s*?")

_extension_pragma_re_u = re.compile(
    r'\s*#\s*(?P<action>[+-])(?P<ext>[^(\s]+)\s*(\((?P<params>.*)\))?[^\S\n]*?')


class Activation:
    """This sort of instances tell us
    whether an extension is enabled at a specific line number"""

    def __init__(self):
        self.intervals = []

    def enable(self, line: int):
        intervals = self.intervals
        if not intervals:
            intervals.append(line)
            return
        if isinstance(intervals[-1], int):
            # already enabled
            return

        intervals.append(line)

    def disable(self, line: int):
        intervals = self.intervals
        if not intervals or isinstance(intervals[-1], range):
            # already disabled
            return
        enable_line = intervals.pop()
        intervals.append(range(enable_line, line))

    def __contains__(self, item):
        for each in self.intervals:
            if isinstance(each, int):
                if item >= each:
                    return True
            else:
                assert isinstance(each, range)
                if item in each:
                    return True
        return False


class ExtensionNotFoundError(Exception):
    pass


class ExtensionMeta(type):
    def __new__(mcs, name, bases, ns: dict):
        if ns.get('_root', False):
            return super().__new__(mcs, name, bases, ns)
        bases = tuple(filter(lambda it: Extension is not it, bases))

        # All extensions need instantiating the its activation info.
        __init__ = ns.get('__init__', None)
        if __init__:
            def init(self, *args, **kwargs):
                self.activation = Activation()
                __init__(self, *args, **kwargs)
        else:
            def init(self):
                self.activation = Activation()
        if 'activation' not in ns:
            ns['activation'] = None

        assert 'identifier' in ns, "An extension should have its identifier."

        ns['__init__'] = init

        ret = type(name, (*bases, RealExtension), ns)  # type: t.Type[RealExtension]
        Registered.extensions[ret.identifier] = ret

        return ret


class RealExtension:
    """
    An abstraction among syntax extensions
    """
    @property
    def activation(self) -> Activation:
        raise NotImplemented

    @property
    @abc.abstractmethod
    def identifier(cls):
        "A string to indicate the class of extension instance."
        raise NotImplemented

    def pre_rewrite_src(self, io: StringIO):
        pass

    @abc.abstractmethod
    def rewrite_ast(self, node: ast.AST):
        "A function to perform AST level rewriting"
        raise NotImplemented

    def post_rewrite_src(self, io: StringIO):
        pass


class Extension(metaclass=ExtensionMeta):
    """automatically extension"""

    _root = True

    @property
    def activation(self) -> Activation:
        raise NotImplemented

    @property
    @abc.abstractmethod
    def identifier(cls):
        "A string to indicate the class of extension instance."
        raise NotImplemented

    def pre_rewrite_src(self, io: StringIO):
        pass

    @abc.abstractmethod
    def rewrite_ast(self, node: ast.AST):
        "A function to perform AST level rewriting"
        raise NotImplemented

    def post_rewrite_src(self, io: StringIO):
        pass


class Registered:
    extensions = {}  # type: t.Dict[str, t.Type[Extension]]


def extract_pragmas(lines):
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


def _stack_exc(f):
    def apply(source_code, filename='<unknown>'):
        try:
            return f(source_code, filename)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            raise e

    return apply


def check_if_use_moshmosh_sys(source_code):
    str_type = type(source_code)
    extension_token = _extension_token_b if str_type is bytes else _extension_token_u
    return bool(extension_token.match(source_code))


@_stack_exc
def perform_extension(source_code, filename):

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
    string_io.write("""
import ast as _ast
def _literal_to_ast(literal):
    '''
    Convert a python literal to an AST.
    '''
    if isinstance(literal, dict):
        ctor = literal.pop('constructor')
        ctor = getattr(_ast, ctor)
        return ctor(**{k: _literal_to_ast(v) for k, v in literal.items()})

    if isinstance(literal, list):
        return list(map(_literal_to_ast, literal))

    return literal

    """)
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
