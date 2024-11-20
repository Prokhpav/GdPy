from typing import Protocol, runtime_checkable, Self
from .gd_module import GdIdRef, GdIdType

__all__ = (
    'GroupConvertible',
    'Group',
    'BlockConvertible',
    'Block',
    'ItemConvertible',
    'Item',
    'TimerConvertible',
    'Timer',
)


@runtime_checkable
class GroupConvertible(Protocol):
    def __gd_group__(self) -> "Group": ...


class Group(GdIdRef, GroupConvertible, constants={0: 'Empty'}):
    Empty: Self  # = Group(0)

    def __new__(cls, value: int | GroupConvertible | None = None) -> "Group":
        if isinstance(value, int) or value is None:
            return cls.type.create(value)
        if isinstance(value, GroupConvertible):
            return value.__gd_group__()
        raise TypeError()

    def __gd_group__(self) -> "Group":
        return self


@runtime_checkable
class BlockConvertible(Protocol):
    def __gd_block__(self) -> "Block": ...


class Block(GdIdRef, BlockConvertible, constants={0: 'Empty'}):
    Empty: Self  # = Block(0)

    def __new__(cls, value: int | BlockConvertible | None = None) -> "Block":
        if isinstance(value, int) or value is None:
            return cls.type.create(value)
        if isinstance(value, BlockConvertible):
            return value.__gd_block__()
        raise TypeError()

    def __gd_block__(self) -> "Block":
        return self


@runtime_checkable
class ItemConvertible(Protocol):
    def __gd_item__(self) -> "Item": ...


class Item(GdIdRef, ItemConvertible, constants={0: 'Empty', -1: 'Points', -2: 'Attempts'}):
    Empty: Self  # = Item(0)
    Points: Self  # = Item(-1)
    Attempts: Self  # = Item(-2)

    def __new__(cls, value: int | ItemConvertible | None = None) -> "Item":
        if isinstance(value, int) or value is None:
            return cls.type.create(value)
        if isinstance(value, ItemConvertible):
            return value.__gd_item__()
        raise TypeError()

    def __gd_item__(self) -> "Item":
        return self


@runtime_checkable
class TimerConvertible(Protocol):
    def __gd_timer__(self) -> "Timer": ...


class Timer(GdIdRef, TimerConvertible, constants={0: 'Empty', -1: 'MainTime'}):
    Empty: Self  # = Timer(-1)
    MainTime: Self  # = Timer(-1)

    def __new__(cls, value: int | TimerConvertible | None = None) -> "Timer":
        if isinstance(value, int) or value is None:
            return cls.type.create(value)
        if isinstance(value, TimerConvertible):
            return value.__gd_timer__()
        raise TypeError()

    def __gd_timer__(self) -> "Timer":
        return self


Group.Empty = Group(0)
Block.Empty = Block(0)
Item.Empty = Item(0)
Item.Points = Item(-1)
Item.Attempts = Item(-2)
Timer.Empty = Timer(0)
Timer.MainTime = Timer(-1)
