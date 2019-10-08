import ast
import typing as t
import typing_extensions as te
from dataclasses import dataclass
T = t.TypeVar('T')
G = t.TypeVar('G')
H = t.TypeVar('H')

runtime_match_failed = "_match_failed"
runtime_match_succeeded = "_match_succeeded"

@dataclass
class Stmts(t.Generic[T]):
    suite: t.List[ast.stmt]


@dataclass
class Expr(t.Generic[T]):
    value: ast.expr


@dataclass
class Symbol(t.Generic[T]):
    name: str
    lineno: int
    col_offset: int

    def to_name(self) -> ast.Name:
        ...


class Pattern(t.Generic[T, G]):
    def __init__(self, f):
        self.f = f

    def apply(self, i: Expr[T], remain: Stmts[G]) -> Stmts[G]:
        ...


class CaseCompilation(t.Generic[G]):
    ret: ast.Name

    def __init__(self, ret_sym: str = ...):
        ...

    def literal(cls, v: T) -> Pattern[T, G]:
        ...

    def pin(self, sym: Expr[T]) -> Pattern[T, G]:
        ...

    def wildcard(cls) -> Pattern[t.Any, G]:
        ...

    def capture(cls, sym: Symbol[T]) -> Pattern[T, G]:
        ...

    def intersect(cls, ps: t.List[Pattern[T, G]]) -> Pattern[T, G]:
        ...

    def alternative(cls, ps: t.List[Pattern[T, G]]) -> Pattern[T, G]:
        ...

    def recog(cls, pattern_maker, item):
        # type: (t.Callable[[Pattern[T, G]], Pattern[T, G]], t.Callable[[Expr[G], int], Expr[H]]) -> t.Callable[[t.List[Pattern[H, G]]], Pattern[T, G]]
        ...

    def recog2(cls, ctor: Expr, elts: t.List[Pattern]) -> Pattern:
        ...

    def size_is(self, n: int) -> t.Callable[[Pattern], Pattern]:
        ...

    @classmethod
    def type_as(cls, a: t.Type[T]):
        def g(b):
            # type: (Pattern[T, G]) -> Pattern[T, G]
            ...

        return g

    @classmethod
    def match(cls, pairs: t.List[t.Tuple[Pattern[T, G], Stmts[G]]]
              ) -> t.Callable[[Expr[T]], Stmts[G]]:
        ...

    def tuple_n(self, elts: t.List[Pattern]) -> Pattern:
        ...

    def list_n(self, elts: t.List[Pattern]) -> Pattern:
        ...

    def item(self, expr: Expr, i) -> Expr:
        ...
