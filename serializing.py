from types import EllipsisType
from typing import Any, ClassVar, TYPE_CHECKING, Literal
from attr import frozen
from attrs import define, field
from collections.abc import Iterator, Callable

from tools.funcs import Factory, extract_unused, factorydict

__all__ = (
    'Base',
    'Sequence',
    'Key',
    'Func',
    'DoNothing',
    'List',
    'WrapKeyInfo',
    'WrapKeys',
    'FieldInfo',
    'MultiField',
    'ToClass',
    'SerializingFamily'
)

_Missed = object()


class Base:
    """
    Two-way conversion. `analyse` and `compile` functions must be inverse to each other.
    However, some unnecessary information can be lost during the process.
    assert data ≈≈ compile(avalyse(data))

    In some cases, if the `compile` method receives a second argument `data`, the compiled information will be inserted into it.

    Can create Sequence of serializers using `>>`: foo >> bar >> baz
    """

    def analyze(self, data):
        raise NotImplementedError()

    def compile(self, value, data=None):
        raise NotImplementedError()

    def get_keys(self) -> Iterator[str]:
        """ get all nested Keys that can be used in serialization. For optimisation reasons. """
        yield from ()

    def _as_sequence(self):
        return (self,)

    def __rshift__(self, other: 'Base'):
        return Sequence(self._as_sequence() + other._as_sequence())


class Sequence(Base):
    """
    Sequentially applies serializers to data. The next one operates on the result of the previous one.
    The first serializer analyses first, compiles last.
    """

    def __init__(self, serializers: tuple[Base, ...]):
        self.serializers = serializers

    def analyze(self, data):
        for szr in self.serializers:
            data = szr.analyze(data)
        return data

    def compile(self, value, data=None):
        for szr in self.serializers[::-1]:
            value = szr.compile(value, data)
        return value

    def get_keys(self) -> Iterator[str]:
        for szr in self.serializers:
            yield from szr.get_keys()

    def _as_sequence(self):
        return self.serializers


class Key(Base):
    """
    Extracts key from dict. Can have a default value.
    In compilation adds value to second argument.
    """

    def __init__(self, key: str, default: Any = _Missed):
        self.key = key
        self.default = default

    def analyze(self, data: dict):
        if self.default is not _Missed:
            return data.get(self.key, self.default)
        return data[self.key]

    def compile(self, value, data: dict = None):
        if self.default is _Missed or value != self.default:
            data[self.key] = value

    def get_keys(self) -> Iterator[str]:
        yield self.key


class Func(Base):
    """
    Wrapper around two funcitons - analyser and compiler.
    If the function is None, it does nothing to the value.
    If compiler uses second argument, set compile_data=True.
    Keys for get_keys() optimisation.
    """

    def __init__(self,
                 analyser: Callable[[Any], Any] | None = None,
                 compiler: Callable[[Any], Any] | Callable[[Any, Any], Any] | None = None,
                 keys: tuple[str, ...] = (),
                 compile_data: bool = False
                 ):
        self.analyser = analyser
        self.compiler = compiler
        self.keys = keys
        self.compile_data = compile_data

    def analyze(self, data):
        if self.analyser is None:
            return data
        return self.analyser(data)

    def compile(self, value, data=None):
        if self.compiler is None:
            return value
        if self.compile_data:
            return self.compiler(value, data)
        return self.compiler(value)

    def get_keys(self) -> Iterator[str]:
        yield from self.keys


class DoNothing(Base):
    """ A serializer that... does nothing """

    def analyze(self, data):
        return data

    def compile(self, value, data=None):
        return value


class List(Base):
    def __init__(self, serializer: Base):
        self.serializer = serializer

    def analyze(self, data):
        return [self.serializer.analyze(dt) for dt in data]

    def compile(self, value, data=None):
        return [self.serializer.compile(val, data) for val in value]


# class FieldBase:
#     """
#     Almost like serializer, but analyser also uses second argument mutation rather returning.
#     """
#
#     def analyze(self, data: dict, value: dict):
#         """ Extract information from data and add it to value """
#         raise NotImplementedError()
#
#     def compile(self, value: dict, data: dict):
#         """ Extract information from value and add it to data """
#         raise NotImplementedError()
#
#     def get_keys(self) -> Iterator[str]:
#         yield from ()
#
#
# class Combinable(Base):
#     def combine(self, other: Self) -> Self:
#         raise NotImplementedError()
#
#
# class DictFields(Base, Combinable):
#     """
#     Applies each field to data, returns the resulting dict value.
#     """
#
#     def __init__(self, fields: tuple[FieldBase, ...]):
#         self.fields = fields
#
#     def analyze(self, data: dict):
#         value = {}
#         for field_ in self.fields:
#             field_.analyze(data, value)
#         return value
#
#     def compile(self, value, data=None):
#         if data is None:
#             data = {}
#         for field_ in self.fields:
#             field_.compile(value, data)
#         return data
#
#     def combine(self, other: Self) -> Self:
#         return DictFields(self.fields + tuple(f for f in other.fields if f not in self.f))
#
#
# @define
# class FieldOptimazable(FieldBase):
#     """
#     This field can be optimized in DictFieldsOptimized - if there are no keys of
#         the field.get_keys() in the data, the field's value will not be calculated.
#     value[name] = serializer.analyse(data)
#     """
#     name: str
#     serializer: Base
#
#     def analyze(self, data: dict, value: dict):
#         val = self.serializer.analyze(data)
#         if val is not None:
#             value[self.name] = val
#
#     def compile(self, value: dict, data: dict):
#         val = value.get(self.name, None)
#         self.serializer.compile(val, data)
#
#     def get_keys(self) -> Iterator[str]:
#         yield from self.serializer.get_keys()
#
#
# class DictFieldsOptimized(DictFields):
#     fields: tuple[FieldBase, ...]
#     unused: FieldBase | None
#     unoptimized_fields: tuple[FieldBase, ...]
#     optimized_fields: tuple[FieldOptimazable, ...]
#     from_key: dict[str, FieldOptimazable]
#     from_name: dict[str, FieldOptimazable]
#
#     def __init__(self,
#                  fields: tuple[FieldBase, ...],
#                  unused: FieldBase | None = None
#                  ):
#         self.fields = fields
#         self.unused = unused
#         self.unoptimized_fields = tuple(field_ for field_ in fields if not isinstance(field_, FieldOptimazable))
#         self.optimized_fields = tuple(field_ for field_ in fields if isinstance(field_, FieldOptimazable))
#         self.from_key: dict[str, FieldOptimazable] = {}
#         self.from_name = {}
#         for field_ in self.optimized_fields:
#             for key in field_.get_keys():
#                 self.from_key[key] = field_
#             self.from_name[field_.name] = field_
#
#     def analyze(self, data: dict):
#         value = {}
#         for field_ in self.unoptimized_fields:
#             field_.analyze(data, value)
#
#         unused_keys = {}
#         used_field_names = {}  # ordered set
#         for key, val in data.items():
#             if key in self.from_key:
#                 used_field_names[self.from_key[key].name] = None
#             elif self.unused is not None:
#                 unused_keys[key] = val
#
#         for name in used_field_names:
#             value[name] = self.from_name[name].serializer.analyze(data)
#
#         if unused_keys and self.unused is not None:
#             self.unused.analyze(unused_keys, value)
#
#         return value
#
#     def compile(self, value: dict, data: dict = None):
#         if data is None:
#             data = {}
#
#         unused_keys = {}
#         if self.unused is not None:
#             self.unused.compile(value, unused_keys)
#
#         for name, val in value.items():
#             if name in self.from_key:
#                 self.from_name[name].serializer.compile(val, data)
#
#         for field_ in self.unoptimized_fields:
#             field_.compile(value, data)
#
#         return data
#
#     def get_keys(self) -> Iterator[str]:
#         for field_ in self.fields:
#             yield from field_.get_keys()
#
#     def combine(self, other: Self) -> Self:
#         return DictFieldsOptimized(self.fields + tuple(f for f in other.fields if f not in self.f))
#
#
# class WrapKeyBase:
#     def __init__(self,
#                  old_key: str,
#                  new_key: str,
#                  serializer: FieldBase,
#                  ):
#         self.old_key = old_key
#         self.new_key = new_key
#         self.serializer = serializer
#
#
# class DictFactory[KT, VT](dict[KT, VT]):
#     def __init__(self, default_factory: 'Callable[[DictFactory, KT], VT]', **kwargs):
#         super().__init__(**kwargs)
#         self.default_factory = default_factory
#
#     def __missing__(self, key):
#         return self.default_factory(self, key)
#
#
# class WrapKeys(Base):
#     def __init__(self, keys: tuple[WrapKeyBase]):
#         self.keys = keys
#         self.map_old_key: dict[str, WrapKeyBase] = {}
#         self.map_new_key: dict[str, WrapKeyBase] = {}
#         for key in self.keys:
#             self.map_old_key[key.old_key] = key
#             self.map_new_key[key.new_key] = key
#
#     def _missing(self, data: dict, key: str):
#         return self.map_old_key[key].serializer.analyze(data, None)
#
#     def analyze(self, data: dict):
#         value = DictFactory(self._missing)
#         unused_keys = {}
#         for key, val in data.items():
#             if key in self.map_old_key:
#                 info = self.map_old_key[key]
#                 info.serializer.analyze(data, val)


# class InheritableCombineSequence(Base, Combinable):
#     def __init__(self,
#                  handler: 'HierarchicalHandler',
#                  serializers: tuple[Combinable, ...]
#                  ):
#         self.handler = handler
#         self.serializers = serializers
#
#     def analyze(self, data):
#         for szr in self.serializers:
#             data = szr.analyze(data)
#         return self.analyze(data)
#
#     def compile(self, value, data=None):
#         for szr in self.serializers[::-1]:
#             value = szr.compile(value, data)
#         return value
#
#     def combine(self, other: Self) -> Self:
#         assert self.handler == other.handler
#         serializers = []
#         for szr1, szr2 in zip(self.serializers, other.serializers, strict=True):
#             serializers.append(szr1.combine(szr2))
#         return InheritableCombineSequence(self.handler, serializers)
#
#
# class HierarchicalHandler:
#     def __init__(self):
#         self.sequences: dict[type, InheritableCombineSequence] = {}
#         self.serializers: dict[type, Base] = {}
#
#     def add(self,
#             klass: type[object],
#             *serializers: Combinable,
#             ):


@frozen
class WrapKeyInfo:
    """
    Describes a translation between key in DATA and name in VALUE.
    Behaviour is symmetrical by swapping key <-> name and value <-> data

    The main relation is:
        VALUE[name] = serializer.analyze(DATA[key])
    It goes as far until an operation cannot be executed (no key or got None).

    Checking None without memory optimization (optimize_key is None):
        if key is not None and serializer is not None and key in DATA:
            val = serializer.analyze(DATA[key])
            if name is not None:
                VALUE[name] = val

    The full algorithm:
        if key is not None and serializer is not None and key in DATA:
            val = serializer.analyze(DATA[key])
            if name is not None and (not optimize_name or val != default_value):
                VALUE[name] = val
        elif name is not None and optimize_name is False:
            VALUE[name] = val

    :param optimize_key: True/False/None - saving memory by not writing default to VALUE
        None: doesn't affect the main algorithm.
        True: checks value before saving to VALUE and prevents saving default_value
        False: force to save default_value, event is the key don't exixst in DATA
    :param default_value:
    :param default_data:
        If diven only one of defaults, the second will be generated using serializer if it is not None

    Unused:
        All unused keys from data are being collected to a single key Ellipsis: {...: {key: val}}

    Usages:
        (key, name, serializer) - standart translation between key and name
        (key, None, serializer) - check DATA[key] using serializer.analyze
        (key, None, default_data, optimize_key=False) - set default_data to key
        (..., None, szr.Error)  - raise an error if there are any unsed key
    """
    key: str | EllipsisType | None
    name: str | EllipsisType | None
    serializer: Base | None
    default_data: Any | Factory | None = None
    default_value: Any | Factory | None = None
    optimize_key: bool | None = None
    optimize_name: bool | None = None

    if TYPE_CHECKING:  # for maker
        def __init__(self,
                     key: str | EllipsisType | None = None,
                     name: str | EllipsisType | None = None,
                     serializer: Base | None = None,
                     default_data: Any | Factory | None = None,
                     default_value: Any | Factory | None = None,
                     optimize_key: bool | None = None,
                     optimize_name: bool | None = None,
                     ):
            pass

    def __attrs_post_init__(self):
        if self.key is None and self.name is None:
            raise TypeError("key and name cannot be both None")
        if self.serializer is not None:
            if self.default_value is None and self.default_data is not None:
                object.__setattr__(self, 'default_value', Factory(self._default_value_factory))
            if self.default_data is None and self.default_value is not None:
                object.__setattr__(self, 'default_data', Factory(self._default_data_factory))

    def _default_value_factory(self):
        return self.serializer.analyze(self.default_data)

    def _default_data_factory(self):
        return self.serializer.compile(self.default_value)


class WrapKeys(Base):
    infos: tuple[WrapKeyInfo, ...]

    from_key: dict[str, WrapKeyInfo]
    from_name: dict[str, WrapKeyInfo]
    force_default_keys: dict[str, Any]
    force_default_names: dict[str, Any]

    def __init__(self, *infos: WrapKeyInfo):
        self.infos = infos
        self.from_key = {}
        self.from_name = {}
        self.force_default_keys = {}
        self.force_default_names = {}
        for info in self.infos:
            if info.name is not None:
                if info.name in self.from_name:
                    raise TypeError("name duplication")
                self.from_name[info.name] = info
            if info.key is not None:
                if info.key in self.from_key:
                    raise TypeError("key duplication")
                self.from_key[info.key] = info
            # optimization is False, force value to have defaults.
            if info.name is not None and info.optimize_name is False:
                self.force_default_names[info.name] = info
            if info.key is not None and info.optimize_key is False:
                self.force_default_keys[info.key] = info

    def _missing_name(self, name):
        if name in self.from_name:
            info = self.from_name[name]
            if info.default_value is not None:
                return Factory.unwrap(info.default_value)
        raise KeyError(name)

    def analyze(self, data: dict):
        data, unused = extract_unused(data, self.from_key)
        if Ellipsis in self.from_key:
            data[Ellipsis] = unused
        elif unused:
            raise KeyError(unused)

        value = factorydict(self._missing_name)

        for key, val in data.items():
            info = self.from_key[key]
            if info.name is None:
                if info.serializer is not None:
                    info.serializer.analyze(val)
                continue

            if info.serializer is not None:
                val = info.serializer.analyze(val)
                if not info.optimize_name or val != Factory.unwrap(info.default_value):
                    value[info.name] = val
            elif info.optimize_name is False:
                value[info.name] = Factory.unwrap(info.default_value)
                continue

        for name, info in self.force_default_names.items():
            if name not in value:
                value[name] = Factory.unwrap(info.default_value)

        if Ellipsis in value:
            value.update(value.pop(Ellipsis))

        return value

    def _missing_key(self, key):
        if key in self.from_key:
            info = self.from_key[key]
            if info.default_data is not None:
                return Factory.unwrap(info.default_data)
        raise KeyError(key)

    def compile(self, value: dict, data=None):
        value, unused = extract_unused(value, self.from_name)
        if Ellipsis in self.from_name:
            value[Ellipsis] = unused
        elif unused:
            raise KeyError(unused)

        if data is not None:
            raise TypeError()
        data = factorydict(self._missing_key)

        for name, val in value.items():
            info = self.from_name[name]
            if info.key is None:
                if info.serializer is not None:
                    info.serializer.compile(val)
                continue

            if info.serializer is not None:
                val = info.serializer.compile(val)
                if not info.optimize_key or val != Factory.unwrap(info.default_data):
                    data[info.key] = val
            elif info.optimize_key is False:
                data[info.key] = Factory.unwrap(info.default_data)
                continue

        for key, info in self.force_default_keys.items():
            if key not in data:
                data[key] = Factory.unwrap(info.default_data)

        if Ellipsis in data:
            data.update(data.pop(Ellipsis))

        return data

    def combine(self, other: 'WrapKeys') -> 'WrapKeys':
        infos = tuple(info for info in self.infos if (
                (info.key is None or info.key not in other.from_key) and
                (info.name is None or info.name not in other.from_name)
        ))  # if key or name presents in other, the info will be overriden.
        return WrapKeys(*infos, *other.infos)


@frozen
class FieldInfo:
    name: str | EllipsisType
    serializer: Base | None | Literal[True] = None
    keys: tuple[str, ...] | None = None
    optimize_name: bool = True

    if TYPE_CHECKING:
        def __init__(self,
                     name: str | EllipsisType = None,
                     serializer: Base | None | Literal[True] = None,
                     keys: tuple[str, ...] | None = None,
                     optimize_name: bool = True,
                     ):
            pass

    def __attrs_post_init__(self):
        if self.serializer is True:
            object.__setattr__(self, 'serializer', Key(self.name))
        if self.keys is None:
            object.__setattr__(self, 'keys', tuple(self.serializer.get_keys()))


class MultiField(Base):
    infos: tuple[FieldInfo, ...]
    from_key: dict[str, FieldInfo]
    from_name: dict[str, FieldInfo]
    force_default_names: dict[FieldInfo, None]  # ordered set

    def __init__(self, *infos: FieldInfo):
        self.infos = infos
        self.from_key = {}
        self.from_name = {}
        self.force_default_names = {}
        for info in self.infos:
            if info.name is not None:
                self.from_name[info.name] = info
            for key in info.keys:
                self.from_key[key] = info
            if not info.optimize_name:
                self.force_default_names[info] = None

    def analyze(self, data: dict):
        data, unused = extract_unused(data, self.from_key)
        if Ellipsis in self.from_key:
            data[Ellipsis] = unused
        elif unused:
            raise KeyError(unused)

        value = {}

        used_fields = dict(self.force_default_names)  # ordered set
        for key in data:
            used_fields[self.from_key[key]] = None

        for info in used_fields:
            if info.name is None:
                if info.serializer is not None:
                    info.serializer.analyze(data)
                continue
            if info.serializer is not None:
                value[info.name] = info.serializer.analyze(data)

        if Ellipsis in value:
            value.update(value.pop(Ellipsis))

        return value

    def compile(self, value: dict, data=None):
        value, unused = extract_unused(value, self.from_key)
        if Ellipsis in self.from_key:
            value[Ellipsis] = unused
        elif unused:
            raise KeyError(unused)

        if data is None:
            data = {}

        used_fields = {}  # ordered set
        for name in value:
            used_fields[self.from_name[name]] = None

        for info in used_fields:
            if info.serializer is not None:
                val = value.get(info.name)
                info.serializer.compile(val, data)

        if Ellipsis in data:
            data.update(data.pop(Ellipsis))

        return data

    def combine(self, other: 'MultiField') -> 'MultiField':
        infos = tuple(info for info in self.infos if (
            (info.name is None or info.name not in other.from_name)
        ))  # if name presents in other, the info will be overriden.
        return MultiField(*infos, *other.infos)


class ToClass(Base):
    def __init__(self, klass: type[object]):
        self.klass = klass
        self.has_dict = '__dict__' in dir(klass)

    def analyze(self, data: dict):
        obj = object.__new__(self.klass)
        if self.has_dict:
            object.__setattr__(obj, '__dict__', data)
            return obj
        for key, val in data.items():
            object.__setattr__(obj, key, val)
        return obj

    def compile(self, value, data=None):
        if self.has_dict:
            return value.__dict__
        return {name: getattr(value, name) for name in value.__class__.__slots__}


@define
class SerializingFamily:
    _dct: dict[Any, Base | Any] = field(init=False, factory=dict)
    _all: ClassVar[dict[str, 'SerializingFamily']] = {}

    def __getitem__(self, key) -> Base:
        return self._dct[key]

    def __setitem__(self, key, value: Base):
        self._dct[key] = value

    @classmethod
    def register(cls, name) -> 'SerializingFamily':
        assert name not in cls._all
        s = cls._all[name] = SerializingFamily()
        return s

    @classmethod
    def get(cls, name) -> 'SerializingFamily':
        return cls._all[name]
