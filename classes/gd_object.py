from typing import ClassVar

from attrs import define as define_gd
from python.attrs_wrap import define_gd, field
from ignore_default import IgnoreDefault
from tools.vector2 import Vector2
from data.special_ids import special_ids


@define_gd
class GdObjectBase(IgnoreDefault):
    x: float


@define_gd
class AnyId(IgnoreDefault):
    id: int = field()


@define_gd
class SpecialId(IgnoreDefault):
    __id__: ClassVar[int] = None

    @property
    def id(self) -> int:
        return self.__class__.__id__

    @id.setter
    def id(self, id: int):
        raise AttributeError(f'id of {self.__class__.__name__} cannot be changed')

    def __init_subclass__(cls, **kwargs):
        if getattr(cls, '__id__', None) is None:
            cls.__id__ = special_ids.inv[cls.__name__]
        super().__init_subclass__(**kwargs)


@define_gd
class GdObjectAnyId(GdObjectBase, AnyId):
    pass


HasId = GdObjectAnyId | SpecialId
