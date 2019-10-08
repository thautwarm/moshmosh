# moshmosh?
# +template-python
import ast
import typing as t
from moshmosh.extensions.pattern_matching.runtime import NotExhaustive
from toolz import compose
T = t.TypeVar('T')
G = t.TypeVar('G')
H = t.TypeVar('H')

runtime_match_failed = "_match_failed"
runtime_match_succeeded = "_match_succeeded"

match_failed = ast.Name("_match_failed", ast.Load())
match_succeeded = ast.Name("_match_succeeded", ast.Load())

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

    def gen(self) -> ast.Name:
        i = self.names[self.base]
        self.names[self.base] += 1
        return ast.Name('{}.{}'.format(self.base, i), ast.Load())


class Expr(t.Generic[T]):
    value: ast.expr

    def __init__(self, mk: ast.expr):
        self.value = mk


class Stmts(t.Generic[T]):
    suite: t.List[ast.stmt]

    def __init__(self, mk: t.List[ast.stmt]):
        self.suite = mk


class Symbol(t.Generic[T]):
    def __init__(self, name, lineno, col_offset):
        self.name = name
        self.lineno = lineno
        self.col_offset = col_offset

    def to_name(self):
        return ast.Name(
            self.name,
            ast.Load(),
            lineno=self.lineno,
            col_offset=self.col_offset)


class Pattern(t.Generic[T, G]):
    def __init__(self, f):
        self.f = f

    def apply(self, i: Expr[T], remain: Stmts[G]) -> Stmts[G]:
        return self.f(i, remain)


def dyn_check(f):
    def func(a, b):
        assert isinstance(a, Expr), (f, type(a))
        assert isinstance(b, Stmts), (f, type(b))
        c = f(a, b)
        assert isinstance(c, Stmts), (f, type(c))
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
        def pat(target: Expr, remain: Stmts):
            stmts = quote_eq(self.ret, v, match_failed, target.value,
                             remain.suite)
            return Stmts(stmts)

        return Pattern(pat)

    def pin(self, s: Expr):
        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_eq(ret, v, failed, expr, stmts):
            if v == expr:
                stmts
            else:
                ret = failed

        @dyn_check
        def pat(target: Expr, remain: Stmts):
            stmts = quote_eq(self.ret, s.value, match_failed, target.value,
                             remain.suite)
            return Stmts(stmts)

        return Pattern(pat)

    def wildcard(_):
        @dyn_check
        def pat(_, remain):
            return remain

        return Pattern(pat)

    # noinspection PyStatementEffect
    def capture(_, sym: Symbol):
        lhs = sym.to_name()

        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_capture(lhs, target, remain):
            lhs = target
            remain

        @dyn_check
        def pat(target: Expr, remain: Stmts):
            stmts = quote_capture(lhs, target.value, remain.suite)
            return Stmts(stmts)

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
            then_code = Stmts(quote_match_failed(not_exhaustive_err_type))
            for each in reversed(ps):
                now_code: Stmts = each.apply(target, body)
                assert isinstance(now_code, Stmts)
                stmts = quote_alt(cur, now_code.suite, then_code.suite,
                                  self.ret, match_failed)
                then_code = Stmts(stmts)
            return then_code

        return Pattern(pat)

    def recog(self, maker, item):
        def pmk(elts: t.List[Pattern]):
            @dyn_check
            def pat(target, body):
                n = len(elts)
                last = body
                mid = Gensym("recog").gen()
                for i in reversed(range(n)):
                    sub_tag: Expr = item(target, i)
                    assert isinstance(sub_tag, Expr)
                    last: Stmts = elts[i].apply(Expr(mid), last)
                    last = Stmts(
                        [ast.Assign([mid], sub_tag.value), *last.suite])
                return last

            return maker(Pattern(pat))

        return pmk

    def recog2(self, ctor: Expr, elts: t.List[Pattern]):
        """
        for deconstructors
        """

        @dyn_check
        def pat(target: Expr, body: Stmts):
            mid = Gensym("decons").gen()
            n = len(elts)

            # noinspection PyStatementEffect PyUnusedLocal
            @quote
            def decons(mid, ret, failed, ctor, n, tag, body):
                mid = ctor.__match__(n, tag)
                if mid is None:
                    ret = failed
                else:
                    body

            inner = self.tuple_n(elts)
            stmts = inner.apply(Expr(mid), body)
            # noinspection PyTypeChecker
            suite = decons(mid, self.ret, match_failed, ctor.value,
                           ast.Constant(n), target.value, stmts.suite)
            return Stmts(suite)

        return Pattern(pat)

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
            def pat(target: Expr, remain: Stmts):
                remain = pattern.apply(target, remain)
                stmts = quote_tychk(self.ret, match_failed, target.value, ty,
                                    remain.suite)
                return Stmts(stmts)

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
            def pat(target: Expr, remain: Stmts):
                remain = pattern.apply(target, remain)
                # noinspection PyTypeChecker
                stmts = quote_size_chk(self.ret, match_failed, target.value, n,
                                       remain.suite)
                return Stmts(stmts)

            return Pattern(pat)

        return then

    def tuple_n(self, elts):
        return self.recog(
            compose(self.type_as(tuple), self.size_is(len(elts))),
            self.item)(elts)

    def list_n(self, elts):
        return self.recog(
            compose(self.type_as(list), self.size_is(len(elts))),
            self.item)(elts)

    def item(self, expr: Expr, i):
        @quote
        def get_item(value, ith):
            # noinspection PyStatementEffect
            value[ith]

        # noinspection PyTypeChecker
        expr: ast.Expr = get_item(expr.value, ast.Constant(i))[0]
        return Expr(expr.value)

    def match(self, pairs):
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

        def pat(target):
            cur = Gensym("switch").gen()
            then_code = Stmts(quote_match_failed(not_exhaustive_err_type))
            for each, body in reversed(pairs):

                suite = body.suite
                suite.reverse()
                suite.append(ast.Assign([self.ret], match_succeeded))
                suite.reverse()

                now_code: Stmts = each.apply(target, body)
                assert isinstance(now_code, Stmts)
                stmts = quote_alt(cur, now_code.suite, then_code.suite,
                                  self.ret, match_failed)
                then_code = Stmts(stmts)
            return then_code

        return pat


# from astpretty import pprint
#
# case_comp = CaseCompilation(".this")
# p1 = case_comp.literal(17)
# p2 = case_comp.capture(Symbol("a"))
# p3 = case_comp.alternative([p1, p2])
#
#
# def expr_code(a):
#     return Expr(a)
#
#
# def stmts_code(xs):
#     return Stmts(xs)
#
#

#
#
# p4 = case_comp.recog(tuple_n(2), item)([p3, case_comp.pin(Symbol("a"))])
#
# k = p4.apply(
#     expr_code(ast.Name("tuple_sized_2", ast.Load())),
#     stmts_code([
#         ast.Name("a", ast.Load()),
#     ]))
#
# from rbnf_rts.unparse import Unparser
# Unparser(ast.Module(k.suite))
