from typing import Protocol, runtime_checkable
from .gd_module import GdIdRef, GdIdType

__all__ = (
    'GroupConvertible',
    'Group',
    'BlockConvertible',
    'Block',
    'ItemConvertible',
    'Item',
)


@runtime_checkable
class GroupConvertible(Protocol):
    def __gd_group__(self) -> "Group": ...


class Group(GdIdRef, GroupConvertible):
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


class Block(GdIdRef, BlockConvertible):
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


class Item(GdIdRef, ItemConvertible):
    def __new__(cls, value: int | ItemConvertible | None = None) -> "Item":
        if isinstance(value, int) or value is None:
            return cls.type.create(value)
        if isinstance(value, ItemConvertible):
            return value.__gd_item__()
        raise TypeError()

    def __gd_item__(self) -> "Item":
        return self
