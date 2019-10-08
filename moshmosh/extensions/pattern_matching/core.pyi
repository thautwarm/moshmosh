import typing as t
import typing_extensions as te
T = t.TypeVar('T')
G = t.TypeVar('G')
H = t.TypeVar('H')


class Code(t.Generic[T]):
    pass


class Symbol(t.Generic[T]):
    pass


class Pattern(t.Generic[T, G]):
    def __init__(self, f):
        self.f = f

    def apply(self, i: Code[T], remain: Code[G]) -> Code[G]:
        ...


class CaseCompilation(t.Generic[G]):
    def literal(cls, v: T) -> Pattern[T, G]:
        ...

    def pin(self, sym: Symbol[T]) -> Pattern[T, G]:
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
        # type: (t.Callable[[Pattern[T, G]], Pattern[T, G]], t.Callable[[Code[G], int], Code[H]]) -> t.Callable[[t.List[Pattern[H, G]]], Pattern[T, G]]
        ...

    @classmethod
    def type_as(cls, a: t.Type[T]):
        def g(b):
            # type: (Pattern[T, G]) -> Pattern[T, G]
            ...

        return g

    @classmethod
    def match(cls, pairs: t.List[Pattern[T, G]]) -> Pattern[T, G]:
        ...
