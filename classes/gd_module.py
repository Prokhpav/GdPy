from attrs import define, field
from typing import TypeVar, Generic, Self, TYPE_CHECKING, Type, ClassVar
from bidict import bidict
from context import Contextable
import weakref

if TYPE_CHECKING:
    from classes.gd_object import GdObjectAnyId

@define(eq=False, init=False, slots=True, repr=False)
class GdIdRef:
    """ Isn't hashable """
    type: ClassVar["GdIdType[Self]"] = field()
    ref: "GdId[Self]" = field()

    if TYPE_CHECKING:
        def __init__(self, value = None):
            pass

    def __safe_init__(self, ref: "GdId[Self]"):
        """ I can't use __init__ because it's called after __new__ every time """
        self.ref = ref
        self.ref.wrefs.add(GdIdWeakRef(self))

    def absorb(self, other: Self):
        self.ref.absorb(other.ref)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.ref is self.ref

    # def __hash__(self):
    #     """ I know this is bad, but good hash isn't compatible with absorbing
    #         So dict[GdIdRef] works at linear speed """
    #     return hash(self.__class__)

    def __del__(self):
        self.ref.wrefs.remove(GdIdWeakRef(self))

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        GdIdType.all[cls] = cls.type = GdIdType(cls)

    def __repr__(self):
        name = self.__class__.__name__
        module = GdModule.C()
        if module is None:
            return f'{name}()'
        val = module.ids[type(self)].values.get(self.ref, None)
        if val is None:
            return f'{name}()'
        return f'{name}({val})'

    def __prepr__(self, _):
        return self.__repr__()

TR = TypeVar("TR", bound=GdIdRef)
TR2 = TypeVar("TR2", bound=GdIdRef)

@define(eq=False, slots=True)
class GdIdType(Generic[TR]):
    all: ClassVar[dict] = {}  # dict[Type[TR]] -> TR
    ref_type: Type[TR] = field()

    def create(self, value: int | None = None) -> TR:
        if value is None:
            return GdId(self).get_ref()
        return GdModule.C().ids[self.ref_type].get(value)

    def get_ref(self, gid: "GdId[TR]") -> TR:
        ref: TR = object.__new__(self.ref_type)
        ref.__safe_init__(gid)
        return ref

    # @classmethod
    # def register(cls, tp: Type[TR2]) -> Type[TR2]:
    #     cls.all[tp] = tp.type = cls(tp)
    #     return tp

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

        gid = self.values.inverse.get(value, None)
        if gid is not None:  # already have gid with this value
            return gid.get_ref()

        gid = GdId(self.type)
        gid.containers.add(self)
        self.values[gid] = value
        return gid.get_ref()

    def set_value(self, gid: TR, value: int | None = None):
        gid_ = gid.ref
        old_value = self.values.pop(gid_, None)
        if value is not None:
            if old_value is None:
                gid_.containers.add(self)
            self.values[gid_] = value
            return
        if old_value is not None:
            gid_.containers.remove(self)

    def get_value(self, gid: TR) -> int:
        value = self.values.get(gid, None)
        if value is not None:
            return value
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
