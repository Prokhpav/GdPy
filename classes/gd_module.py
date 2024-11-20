from attrs import define, field
from typing import TypeVar, Generic, Self, TYPE_CHECKING, Type, ClassVar
from bidict import bidict
from context import Contextable
import weakref

from python.named_const import Default

if TYPE_CHECKING:
    from classes.gd_object import GdObjectAnyId

@define(eq=False, init=False, slots=True, repr=False)
class GdIdRef:
    """ Isn't hashable """
    type: ClassVar["GdIdType[Self]"] = field()
    ref: "GdId[Self]" = field()

    if TYPE_CHECKING:
        def __init__(self, value=None):
            pass

    def is_constant(self) -> bool:
        return self.ref in self.type.constants.inv

    def get_constant_name(self) -> str | None:
        if not self.is_constant():
            return None
        return self.type.constants_names[self.type.constants.inv[self.ref]]

    def __safe_init__(self, ref: "GdId[Self]"):
        """ I can't use __init__ because it's called after __new__ every time """
        self.ref = ref
        self.ref.wrefs.add(GdIdWeakRef(self))

    def get_value(self, default=Default):
        if self.is_constant():
            return self.type.constants.inv[self.ref]
        if default is not Default and GdModule.C(None) is None:
            return default
        return GdModule.C().ids[self.__class__].get_value(self, default)

    def absorb(self, other: Self):
        self.ref.absorb(other.ref)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.ref is self.ref

    def __del__(self):
        self.ref.wrefs.remove(GdIdWeakRef(self))

    def __init_subclass__(cls, constants: dict[int, str | None] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        assert isinstance(constants, dict)
        GdIdType.all[cls] = cls.type = GdIdType(cls, constants)

    def __repr__(self):
        cls_name = self.__class__.__name__
        name = self.get_constant_name()
        if name is not None:
            return f"{cls_name}.{name}"
        val = self.get_value(None)
        if val is None:
            return f'{cls_name}()'
        return f'{cls_name}({val})'

    def __prepr__(self, _):
        return self.__repr__()

TR = TypeVar("TR", bound=GdIdRef)
TR2 = TypeVar("TR2", bound=GdIdRef)

@define(eq=False, slots=True)
class GdIdType(Generic[TR]):
    all: ClassVar[dict] = {}  # dict[Type[TR]] -> TR
    ref_type: Type[TR] = field()
    constants_names: dict[int, str | None]
    constants: 'bidict[int, GdId[TR]]' = field(init=False)

    def __attrs_post_init__(self):
        self.constants = bidict({value: self.create().ref for value in self.constants_names})

    def create(self, value: int | None = None) -> TR:
        if value is None:
            return GdId(self).get_ref()
        if value in self.constants:
            return self.constants[value].get_ref()
        return GdModule.C().ids[self.ref_type].get(value)

    def get_ref(self, gid: "GdId[TR]") -> TR:
        ref: TR = object.__new__(self.ref_type)
        ref.__safe_init__(gid)
        return ref

    @classmethod
    def ids_factory(cls):
        return {tp: GdIdContainer(gid_tp) for tp, gid_tp in GdIdType.all.items()}

class GdIdWeakRef(weakref.ref[TR]):
    if TYPE_CHECKING:
        def __call__(self) -> TR:
            ...

    def __eq__(self, other):
        return isinstance(other, GdIdWeakRef) and self() is other()

    def __hash__(self):
        return id(self())

@define(eq=False, slots=True)
class GdId(Generic[TR]):
    type: GdIdType[TR] = field()
    wrefs: set[GdIdWeakRef[TR]] = field(init=False, factory=set, repr=False)  # assert cls.wrefs[i]().ref is cls
    containers: set['GdIdContainer[TR]'] = field(init=False, factory=set)  # assert cls in cls.containers[i].values and cls.type == cls.containers[i].type

    def __eq__(self, other):
        return other is self

    def __hash__(self):
        return id(self)  # be careful when absorbing! - that's why I added containers set

    def get_ref(self):
        for wref in self.wrefs:
            return wref()
        return self.type.get_ref(self)

    def absorb(self, other: Self):
        """
        Combines two gd_ids. If 'serializer' have value in some module and 'cls' haven't, will inherit that value
        """
        if not isinstance(other, GdId):
            raise TypeError(f"Can't absorb {type(other)}")
        if self.type != other.type:
            raise TypeError(f"Can't absorb different type: {self.type!r} != {other.type!r}")
        if other in self.type.constants.inv:
            raise TypeError(f"Can't absorb constant gdid")

        for wref in list(other.wrefs):  # copying wrefs to prevent deleting while iterating
            ref = wref()
            if ref is not None:
                ref.ref = self
                self.wrefs.add(wref)
        other.wrefs.clear()

        for container in other.containers:
            value = container.values.pop(other)
            if self not in container.values:
                self.containers.add(container)
                container.values[self] = value
        del other

@define(slots=True)
class GdIdContainer(Generic[TR]):
    type: GdIdType[TR] = field()
    values: bidict[GdId[TR], int] = field(init=False, factory=bidict)
    _next_free: int = field(init=False, default=1)

    def __hash__(self):
        return id(self)

    def get(self, value: int | None = None) -> TR:
        if value is None:
            return GdId(self.type).get_ref()
        if value in self.type.constants:
            return self.type.constants[value].get_ref()

        gid = self.values.inverse.get(value, None)
        if gid is not None:  # already have gid with this value
            return gid.get_ref()

        gid = GdId(self.type)
        gid.containers.add(self)
        self.values[gid] = value
        return gid.get_ref()

    def set_value(self, gid: TR, value: int | None = None):
        if gid.is_constant():
            raise TypeError("Constant gdid can't change value")
        gid_ = gid.ref
        old_value = self.values.pop(gid_, None)
        if value is not None:
            if old_value is None:
                gid_.containers.add(self)
            self.values[gid_] = value
            return
        if old_value is not None:
            gid_.containers.remove(self)

    def get_value(self, gid: TR, default: int = Default) -> int:
        if gid.is_constant():
            return gid.type.constants.inv[gid.ref]
        value = self.values.get(gid.ref, None)
        if value is not None:
            return value
        if default is not Default:
            return default
        while self._next_free in self.values.inverse:
            self._next_free += 1
        value = self._next_free
        self.set_value(gid, value)
        self._next_free += 1
        return value

@define(slots=True)
class GdModule(Contextable):
    objects: list["GdObjectAnyId"] = field(init=False, factory=list)
    ids: dict[Type[TR], GdIdContainer[TR]] = field(init=False, factory=GdIdType.ids_factory)

    # if TYPE_CHECKING:
    #     @property  # pycharm is pretty stupid at typing
    #     def ids(self) -> dict[Type[TR], GdIdContainer[TR]]:
    #         return ...
