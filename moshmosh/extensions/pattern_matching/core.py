# moshmosh?
# +template-python
import ast
import typing as t
from moshmosh.extensions.pattern_matching.runtime import NotExhaustive
from toolz import compose
T = t.TypeVar('T')
G = t.TypeVar('G')
H = t.TypeVar('H')


match_failed = ast.Name("_match_failed", ast.Load())
match_succeeded = ast.Name("_match_failed", ast.Load())

not_exhaustive_err_type = ast.Name(NotExhaustive.__name__, ast.Load())


def quote(_):
    raise NotImplemented


class Names(dict):
    def __missing__(self, key):
        v = self[key] = len(self)
        return v


class Gensym:
    names = Names()

    def __init__(self, base_name):
        self.base = base_name

    def gen(self):
        i = self.names[self.base]
        self.names[self.base] += 1
        return '{}.{}'.format(self.base, i)


class Code(t.Generic[T]):
    def __init__(self, mk: t.List[ast.stmt]):
        self.stmts = mk


class Symbol(t.Generic[T]):
    def __init__(self, name):
        self.name = name


class Pattern(t.Generic[T, G]):
    def __init__(self, f):
        self.f = f

    def apply(self, i: Code[T], remain: Code[G]) -> Code[G]:
        return self.f(i, remain)


def dyn_check(f):
    def func(a, b):
        assert isinstance(a, Code), type(a)
        assert isinstance(b, Code), type(b)
        c = f(a, b)
        assert isinstance(c, Code), type(c)
        return c

    return func


class CaseCompilation(t.Generic[G]):
    def __init__(self, ret_sym: str = '.RET'):
        self.ret = ast.Name(ret_sym, ast.Load())

    def literal(self, v):
        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_eq(ret, v, failed, expr, stmts):
            if v == expr:
                stmts
            else:
                ret = failed

        @dyn_check
        def pat(target: Code, remain: Code):
            stmts = quote_eq(self.ret, ast.Constant(v), match_failed,
                             target.stmts[0], remain.stmts)
            return Code(stmts)

        return Pattern(pat)

    def pin(self, s: Symbol):
        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_eq(ret, v, failed, expr, stmts):
            if v == expr:
                stmts
            else:
                ret = failed

        @dyn_check
        def pat(target: Code, remain: Code):
            stmts = quote_eq(self.ret, ast.Name(s.name, ast.Load()),
                             match_failed, target.stmts[0], remain.stmts)
            return Code(stmts)

        return Pattern(pat)

    def wildcard(_):
        @dyn_check
        def pat(_, remain):
            return remain

        return Pattern(pat)

    # noinspection PyStatementEffect
    def capture(_, sym: Symbol):
        lhs = ast.Name(sym.name, ast.Store())

        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_capture(lhs, target, remain):
            lhs = target
            remain

        @dyn_check
        def pat(target, remain):
            stmts = quote_capture(lhs, target.stmts[0], remain.stmts)
            return Code(stmts)

        return Pattern(pat)

    def intersect(_, ps):
        @dyn_check
        def pat(target, body):
            for p in reversed(ps):
                body = p.apply(target, body)
            return body

        return Pattern(pat)

    def alternative(self, ps):
        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_alt(cur, now_stmts, then_stmts, ret, failed):
            now_stmts
            cur = ret
            if cur is failed:
                then_stmts
            else:
                ret = cur

        @quote
        def quote_match_failed(not_exhaustive_err_type):
            raise not_exhaustive_err_type

        @dyn_check
        def pat(target, body):
            cur = Gensym("or").gen()
            cur = ast.Name(cur, ast.Load())
            then_code = Code(quote_match_failed(not_exhaustive_err_type))
            for each in reversed(ps):
                now_code: Code = each.apply(target, body)
                assert isinstance(now_code, Code)
                stmts = quote_alt(cur, now_code.stmts, then_code.stmts,
                                  self.ret, match_failed)
                then_code = Code(stmts)
            return then_code

        return Pattern(pat)

    def recog(self, maker, item):
        def pmk(elts: t.List[Pattern]):
            @dyn_check
            def pat(target, body):
                n = len(elts)
                last = body
                for i in reversed(range(n)):
                    sub_tag = item(target, i)
                    last = elts[i].apply(sub_tag, last)
                return last

            return maker(Pattern(pat))

        return pmk

    def type_as(self, ty):
        if isinstance(ty, type):
            ty = ty.__name__
        ty = ast.Name(ty, ast.Load())

        def then(pattern):
            # noinspection PyStatementEffect PyUnusedLocal
            @quote
            def quote_tychk(ret, failed, tag, ty, stmts):
                if isinstance(tag, ty):
                    stmts
                else:
                    ret = failed

            @dyn_check
            def pat(target: Code, remain: Code):
                remain = pattern.apply(target, remain)
                stmts = quote_tychk(self.ret, match_failed, target.stmts[0],
                                    ty, remain.stmts)
                return Code(stmts)

            return Pattern(pat)

        return then

    def size_is(self, n: int):
        n = ast.Constant(n)

        def then(pattern):
            if -5 < n.value < 256:
                # noinspection PyStatementEffect PyUnusedLocal
                @quote
                def quote_size_chk(ret, failed, tag, n, stmts):
                    if len(tag) is n:
                        stmts
                    else:
                        ret = failed
            else:
                # noinspection PyStatementEffect PyUnusedLocal
                @quote
                def quote_size_chk(ret, failed, tag, n, stmts):
                    if len(tag) == n:
                        stmts
                    else:
                        ret = failed

            @dyn_check
            def pat(target: Code, remain: Code):
                remain = pattern.apply(target, remain)
                # noinspection PyTypeChecker
                stmts = quote_size_chk(self.ret, match_failed,
                                       target.stmts[0], n, remain.stmts)
                return Code(stmts)

            return Pattern(pat)

        return then


from astpretty import pprint

case_comp = CaseCompilation(".this")
p1 = case_comp.literal(17)
p2 = case_comp.capture(Symbol("a"))
p3 = case_comp.alternative([p1, p2])


def expr_code(a):
    return Code([a])


def stmts_code(xs):
    return Code(xs)


recog = compose(case_comp.type_as(tuple), case_comp.size_is(2))


def item(code: Code, i):
    @quote
    def get_item(value, ith):
        # noinspection PyStatementEffect
        value[ith]

    # noinspection PyTypeChecker
    return Code(get_item(code.stmts[0], ast.Constant(i)))


p4 = case_comp.recog(recog, item)([p3, case_comp.pin(Symbol("a"))])

k = p4.apply(
    expr_code(ast.Name("tuple_sized_2", ast.Load())),
    stmts_code([
        ast.Name("a", ast.Load()),
    ]))

from rbnf_rts.unparse import Unparser
Unparser(ast.Module(k.stmts))
