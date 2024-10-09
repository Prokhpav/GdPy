from typing import Any, Callable, ClassVar, TYPE_CHECKING, TypeVar

from attr import Attribute
from attrs import define, field, NOTHING, Factory

from python.tools import map_default
from python.named_const import Missed
from context import Contextable

__all__ = ('DefaultField', 'SafeGet', 'IgnoreDefault')

T = TypeVar("T")
Factory: Any

@define(kw_only=True, slots=True)
class DefaultField:
    name: str = field(init=False)
    default: Any | Factory = field(default=Missed)
    factory: Callable[[], Any] | Callable[[Any], Any] = field(default=Missed)
    takes_self: bool = field(default=Missed)
    mutable: bool = field(default=False)

    def __attrs_post_init__(self):
        if self.default is not Missed and self.factory is not Missed:
            raise TypeError("Can't be both default and factory")
        if self.default is not Missed and self.mutable:
            raise TypeError("Default field value is mutable")
        if self.takes_self is not Missed:
            if self.factory is Missed:
                raise TypeError("Takes self applies only to factory")

    def get(self, instance):
        if not self.mutable:
            if self.default is not Missed:
                return self.default
            if self.factory is not Missed:
                return self.factory(instance) if self.takes_self else self.factory()
            raise TypeError("No default")
        if self.factory is Missed:
            raise TypeError("No default")
        value = self.factory(instance) if self.takes_self else self.factory()
        if not SafeGet.C():
            instance.__dict__[self.name] = value
        return value

@define(slots=True)
class SafeGetClass(Contextable):
    _value: bool = field()

    @property
    def Not(self):
        return SafeGetClass(not self._value)

    def __bool__(self):
        return self._value

    def __invert__(self):
        return self.Not

    def __getitem__(self, item: T) -> T:
        return SafeGetWrapper(self, item)

SafeGet = SafeGetClass(True)

class SafeGetWrapper:
    def __init__(self, get, obj):
        self.__getter = get
        self.__object = obj

    def __getattr__(self, name):
        with self.__getter:
            return getattr(self.__object, name)

if TYPE_CHECKING:
    def SafeGetWrapper(obj: T) -> T:
        return obj

#

class IgnoreDefaultMeta(type):
    __default_fields__: dict[str, DefaultField]
    __attrs_attrs__: tuple[Attribute]

    def __new__(mcs, cls_name, cls_bases, cls_dict: dict, **kwargs):
        __cls = type.__new__(mcs, cls_name, cls_bases, cls_dict, **kwargs)
        if '__attrs_attrs__' in cls_dict:  # recreated via define(slots=True)
            __cls.__init_default_fields__()
        return __cls

    def __setattr__(cls, key, value):
        type.__setattr__(cls, key, value)
        if key == '__match_args__':  # created via define(slots=False)
            cls.__init_default_fields__()

    def __init_default_fields__(cls):
        fields = {}
        for base in cls.__bases__[::-1]:
            fields.update(getattr(base, '__default_fields__', {}))
        for attribute in cls.__attrs_attrs__:
            if attribute.default is not NOTHING:
                dct = {}
                if isinstance(attribute.default, Factory):
                    dct['factory'] = attribute.default.factory
                    dct['takes_self'] = attribute.default.takes_self
                    dct['mutable'] = True
                else:
                    dct['default'] = attribute.default
                field = DefaultField(**dct)
                field.name = attribute.name
                fields[attribute.name] = field
        for name, field in cls.__dict__.get('__default_fields__', {}).items():
            field.name = name
            fields[name] = field
        cls.__default_fields__ = fields

        if cls.__init__.__doc__ in (
                f"Method generated by attrs for class {cls.__qualname__}.",
                "Initialize self.  See help(type(self)) for accurate signature."
        ):
            # attrs-generated init
            def func(name, default):
                if name in cls.__default_fields__:
                    return Missed
                return default

            map_default(cls.__init__, func)

class IgnoreDefault(metaclass=IgnoreDefaultMeta):
    """
    TODO: doc IgnoreDefault
    """
    __default_fields__: ClassVar[dict[str, DefaultField]] = {}

    def _getattr(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self.__class__.__default_fields__:
            return self.__class__.__default_fields__[name].get(self)
        raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {name!r}")

    def _setattr(self, name, value):
        if value is Missed:
            return self.__dict__.pop(name, None)
        object.__setattr__(self, name, value)

    locals()['__getattr__'] = _getattr  # trick stupid PyCharm to highlight 'Unresolved attribute'
    locals()['__setattr__'] = _setattr
    del _getattr, _setattr


if __name__ == '__main__':
    def _main():
        @define
        class Foo(IgnoreDefault):
            bar: list = field(factory=list)

        print(Foo.__init__.__defaults__)  # >>> (Missed,)

        print(Foo.__default_fields__)  # >>> {'bar': DefaultField(factory=list)}

        foo = Foo()

        print(foo.__dict__)  # .       >>> {}

        with SafeGet:
            print(foo.bar)  # .        >>> []
        print(SafeGet[foo].bar)  # .   >>> []

        print(foo.__dict__)  # .       >>> {}

        with ~SafeGet:
            print(foo.bar)  # .        >>> []
        print(SafeGet.Not[foo].bar)  # >>> []

        print(foo.__dict__)  # >>> {'bar': []}

    _main()
