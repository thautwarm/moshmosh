# moshmosh?
# +template-python
import typing as t
from moshmosh.ast_compat import ast, get_constant
from moshmosh.extensions.pattern_matching.runtime import NotExhaustive
from toolz import compose
T = t.TypeVar('T')
G = t.TypeVar('G')
H = t.TypeVar('H')

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
    value = None  # type: ast.expr

    def __init__(self, mk: ast.expr):
        self.value = mk


class Stmts(t.Generic[T]):
    suite = None  # type: t.List[ast.stmt]

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
        def quote_eq(ret, v, expr, stmts):
            if v == expr:
                stmts
            else:
                ret = None  # failed

        @dyn_check
        def pat(target: Expr, remain: Stmts):
            stmts = quote_eq(self.ret, v, target.value,
                             remain.suite)
            return Stmts(stmts)

        return Pattern(pat)

    def pin(self, s: Expr):
        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_eq(ret, v, expr, stmts):
            if v == expr:
                stmts
            else:
                ret = None

        @dyn_check
        def pat(target: Expr, remain: Stmts):
            stmts = quote_eq(self.ret, s.value, target.value,
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
        def quote_alt(now_stmts, then_stmts, ret):
            now_stmts
            if ret is None:
                then_stmts

        @quote
        def quote_match_failed(not_exhaustive_err_type):
            raise not_exhaustive_err_type

        @dyn_check
        def pat(target, body):
            then_code = Stmts(quote_match_failed(not_exhaustive_err_type))
            for each in reversed(ps):
                now_code = each.apply(target, body)  # type: Stmts
                assert isinstance(now_code, Stmts)
                stmts = quote_alt(now_code.suite, then_code.suite,
                                  self.ret)
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
                    sub_tag = item(target, i)  # type: Stmts
                    assert isinstance(sub_tag, Expr)
                    last = elts[i].apply(Expr(mid), last)  # type: : Stmts
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
            def decons(mid, ret, ctor, n, tag, body):
                mid = ctor.__match__(n, tag)
                if mid is None:
                    ret = None
                else:
                    body

            inner = self.seq_n(tuple, elts)
            stmts = inner.apply(Expr(mid), body)
            # noinspection PyTypeChecker
            suite = decons(mid, self.ret, ctor.value,
                           ast.Constant(n), target.value, stmts.suite)
            return Stmts(suite)

        return Pattern(pat)

    def instance_of(self, ty):
        # noinspection PyStatementEffect PyUnusedLocal
        @quote
        def quote_tychk(ret, tag, type, stmts):
            if isinstance(tag, type):
                stmts
            else:
                ret = None

        @dyn_check
        def pat(target: Expr, remain: Stmts):
            stmts = quote_tychk(self.ret, target.value, ty.value,
                                remain.suite)
            return Stmts(stmts)

        return Pattern(pat)

    def type_as(self, ty):
        if isinstance(ty, type):
            ty = ty.__name__
        ty = ast.Name(ty, ast.Load())

        def then(pattern):
            # noinspection PyStatementEffect PyUnusedLocal
            @quote
            def quote_tychk(ret, tag, ty, stmts):
                if isinstance(tag, ty):
                    stmts
                else:
                    ret = None

            @dyn_check
            def pat(target: Expr, remain: Stmts):
                remain = pattern.apply(target, remain)
                stmts = quote_tychk(self.ret, target.value, ty,
                                    remain.suite)
                return Stmts(stmts)

            return Pattern(pat)

        return then

    def size_is(self, n: int):
        n = ast.Constant(n)

        def then(pattern):
            if -5 < get_constant(n) < 256:
                # noinspection PyStatementEffect PyUnusedLocal
                @quote
                def quote_size_chk(ret, tag, n, stmts):
                    if len(tag) is n:
                        stmts
                    else:
                        ret = None
            else:
                # noinspection PyStatementEffect PyUnusedLocal
                @quote
                def quote_size_chk(ret, tag, n, stmts):
                    if len(tag) == n:
                        stmts
                    else:
                        ret = None

            @dyn_check
            def pat(target: Expr, remain: Stmts):
                remain = pattern.apply(target, remain)
                # noinspection PyTypeChecker
                stmts = quote_size_chk(self.ret, target.value, n,
                                       remain.suite)
                return Stmts(stmts)

            return Pattern(pat)

        return then

    def size_ge(self, n: int):
        n = ast.Constant(n)

        def then(pattern):
            @quote
            def quote_size_chk(ret, tag, n, stmts):
                if len(tag) >= n:
                    stmts
                else:
                    ret = None

            @dyn_check
            def pat(target: Expr, remain: Stmts):
                remain = pattern.apply(target, remain)
                # noinspection PyTypeChecker
                stmts = quote_size_chk(self.ret, target.value, n,
                                       remain.suite)
                return Stmts(stmts)

            return Pattern(pat)

        return then

    def seq_n(self, type, elts):
        return self.recog(
            compose(self.type_as(type), self.size_is(len(elts))),
            self.item)(elts)

    def seq_m_star_n(self, type, elts1, star, elts2):
        n1 = len(elts1)
        n2 = len(elts2)
        n = n1 + n2
        if n2 is 0:
            # when elts2 is empty,
            # use a[-1:None] instead of a[-1:-0]
            end = None
        else:
            end = -n2

        def item(expr: Expr, i):
            if i < n1:
                return self.item(expr, i)
            if i > n1:
                return self.item(expr, i - n)

            @quote
            def get_item(value, start, end):
                # noinspection PyStatementEffect
                value[start:end]

            # noinspection PyTypeChecker
            expr = get_item(expr.value, ast.Constant(n1), ast.Constant(end))[0]  # type: ast.Expr
            return Expr(expr.value)

        return self.recog(
            compose(self.type_as(type), self.size_ge(n)),
            item
        )(elts1 + [star] + elts2)

    def item(self, expr: Expr, i):
        @quote
        def get_item(value, ith):
            # noinspection PyStatementEffect
            value[ith]

        # noinspection PyTypeChecker
        expr = get_item(expr.value, ast.Constant(i))[0]  # type: ast.Expr
        return Expr(expr.value)

    def match(self, pairs):
        @quote
        def quote_alt(now_stmts, then_stmts, ret):
            now_stmts
            if ret is None:
                then_stmts

        @quote
        def quote_match_failed(not_exhaustive_err_type):
            raise not_exhaustive_err_type

        def pat(target):
            then_code = Stmts(quote_match_failed(not_exhaustive_err_type))
            for each, body in reversed(pairs):

                suite = body.suite
                suite.reverse()
                suite.append(ast.Assign([self.ret], ast.Constant(())))
                suite.reverse()

                now_code = each.apply(target, body)  # type: Stmts
                assert isinstance(now_code, Stmts)
                stmts = quote_alt(now_code.suite, then_code.suite,
                                  self.ret)
                then_code = Stmts(stmts)
            return then_code

        return pat
