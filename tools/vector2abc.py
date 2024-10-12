from abc import abstractmethod
from collections.abc import Iterator, Callable
from typing import TYPE_CHECKING, ClassVar, Self, Any, Literal, Never
from python.named_const import Default

class Vector2Abc[TGet, TSet]:
    __slots__ = ('x', 'y')

    if TYPE_CHECKING:
        @property
        def x(self) -> TGet:
            ...

        @x.setter
        def x(self, value: TSet) -> None:
            ...

        @property
        def y(self) -> TGet:
            ...

        @y.setter
        def y(self, value: TSet) -> None:
            ...

    @staticmethod
    @abstractmethod
    def __converter__(value: TSet) -> TGet:
        ...

    @property
    @abstractmethod
    def __default__(self) -> TSet:
        ...

    @classmethod
    def __create__(cls, x: TGet, y: TGet) -> Self:
        vec = object.__new__(cls)
        object.__setattr__(vec, 'x', x)
        object.__setattr__(vec, 'y', y)
        return vec

    def __init__(self, x: TSet | type(Default) = Default, y: TSet | type(Default) = Default):
        self.x = self.__default__ if x is Default else x
        self.y = self.__default__ if y is Default else y

    def __setattr__(self, name: str, value: TSet) -> None:
        if isinstance(value, dict):
            pass
        object.__setattr__(self, name, self.__converter__(value))

    def __len__(self) -> Literal[2]:
        return 2

    def __iter__(self) -> Iterator[TGet]:
        yield self.x
        yield self.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __getitem__(self, index: int) -> TGet:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        return (self.x, self.y)[index]

    def __setitem__(self, index: int, value: TSet) -> None:
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            arr = [self.x, self.y]
            arr[index] = value
            self.x, self.y = arr

    def __reversed__(self) -> Self:
        return self.__class__(self.y, self.x)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Vector2Abc) and self.x == other.x and self.y == other.y

    def clone(self) -> Self:
        return self.__create__(self.x, self.y)

    def replace(self, x: TSet | type(Default) = Default, y: TSet | type(Default) = Default) -> Self:
        x = self.x if x is Default else x
        y = self.y if y is Default else y
        return self.__create__(x, y)

# def create_vector_type[TGet, TSet](name: str, converter: Callable[[TSet], TGet], default: TSet) -> type[Vector2Abc[TGet, TSet]]:
#     return type[Vector2Abc](name, (Vector2Abc,), {
#         '__converter__': converter,
#         '__default__': default,
#     })
#
# def get_vector_type[TGet, TSet](converter: Callable[[TSet], TGet]) -> type[Vector2Abc[TGet, TSet]]:
#     return Vector2Abc[TGet, TSet]
