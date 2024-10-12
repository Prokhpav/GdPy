from typing import Self, Any
import math
from tools.vector2abc import Vector2Abc

class Vector2(Vector2Abc[float, Any]):
    __slots__ = ('x', 'y')

    __converter__ = float
    __default__ = 0.

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y)

    def __add__(self, other: Self | tuple[float, float] | Vector2Abc[float, Any]) -> Self:
        x, y = other
        return self.__class__(self.x + x, self.y + y)

    def __sub__(self, other: Self | tuple[float, float] | Vector2Abc[float, Any]) -> Self:
        x, y = other
        return self.__class__(self.x + x, self.y + y)

    def __mul__(self, other: float) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> Self:
        return self.__class__(self.x / other, self.y / other)

    def __floordiv__(self, other: float) -> Self:
        return self.__class__(self.x // other, self.y // other)

    def __mod__(self, other: float) -> Self:
        return self.__class__(self.x % other, self.y % other)

    def dot(self, other: Self | tuple[float, float] | Vector2Abc[float, Any]) -> float:
        x, y = other
        return self.x * x + self.y * y

    def cross(self, other: Self | tuple[float, float] | Vector2Abc[float, Any]) -> Self:
        x, y = other
        return self.x * y - self.y * x

    def __abs__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def length2(self) -> float:
        return self.x ** 2 + self.y ** 2

    def __round__(self, n: int | None = None) -> Self:
        return self.__class__(round(self.x, n), round(self.y, n))

    def __floor__(self) -> Self:
        return self.__class__(math.floor(self.x), math.floor(self.y))

    def __ceil__(self) -> Self:
        return self.__class__(math.ceil(self.x), math.ceil(self.y))

    def __trunc__(self) -> Self:
        return self.__class__(math.trunc(self.x), math.trunc(self.y))

    def __complex__(self) -> complex:
        return complex(self.x, self.y)

    def normalized(self) -> Self:
        return self / abs(self)

    def distance(self, other: Self | tuple[float, float]) -> float:
        return abs(self - other)

class Vector2Int(Vector2Abc[int, Any]):
    __slots__ = ('x', 'y')

    __converter__ = int
    __default__ = 0.

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y)

    def __add__(self, other: Self | tuple[int, int]) -> Self:
        x, y = other
        return self.__class__(self.x + x, self.y + y)

    def __sub__(self, other: Self | tuple[int, int]) -> Self:
        x, y = other
        return self.__class__(self.x + x, self.y + y)

    def __mul__(self, other: int) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> Vector2:
        return Vector2(self.x / other, self.y / other)

    def __floordiv__(self, other: int) -> Self:
        return self.__class__(self.x // other, self.y // other)

    def __mod__(self, other: int) -> Self:
        return self.__class__(self.x % other, self.y % other)

    def dot(self, other: Self | tuple[int, int]) -> int:
        x, y = other
        return self.x * x + self.y * y

    def cross(self, other: Self | tuple[int, int]) -> Self:
        x, y = other
        return self.x * y - self.y * x

    def __abs__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def length2(self) -> float:
        return self.x ** 2 + self.y ** 2

    def __round__(self, n: int | None = None) -> Self:
        return self.__class__(round(self.x, n), round(self.y, n))

    def __complex__(self) -> complex:
        return complex(self.x, self.y)

    def normalized(self) -> Vector2:
        return self / abs(self)

class Vector2Bool(Vector2Abc[bool, bool]):
    __slots__ = ('x', 'y')
    __converter__ = bool
    __default__ = False
