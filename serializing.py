from enum import Enum
from functools import partial
from types import EllipsisType
from typing import Any, ClassVar, TYPE_CHECKING, Literal
from attr import frozen
from attrs import define, field
from collections.abc import Iterator, Callable

from tools.funcs import Factory, factorydict, pairs_to_dict, dict_to_pairs

__all__ = (
    'Base',
    'Sequence',
    'Key',
    'Func',
    'DoNothing',
    'List',
    'Mapping',
    'Tuple',
    'StrSplit',
    'NameTuple',
    'WrapKeyInfo',
    'WrapKeys',
    'FieldInfo',
    'MultiField',
    'ToClass',
    'ToAttrs',
    'ToEnum',
    'SerializingFamily'
)

_Missed = object()


class Base:
    """
    Two-way conversion. `analyze` and `compile` functions must be inverse to each other.
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


class Mapping(Base):
    items: tuple[tuple[Any, Any], ...]
    default_value: Any = _Missed
    default_value_keep: bool = False
    default_data: Any = _Missed
    default_data_keep: bool = False

    def __init__(self,
                 *items: tuple[Any, Any],
                 default_value: Any = _Missed,
                 default_value_keep: bool = False,
                 default_data: Any = _Missed,
                 default_data_keep: bool = False
                 ):
        self.items = items
        self.default_value = default_value
        self.default_value_keep = default_value_keep
        self.default_data = default_data
        self.default_data_keep = default_data_keep
        self._forward: dict = {}
        self._backward: dict = {}
        for a, b in self.items:
            self._forward[a] = b
            self._backward[b] = a

    def analyze(self, data):
        if self.default_value is not _Missed:
            return self._forward.get(data, self.default_value)
        if self.default_value_keep:
            return self._forward.get(data, data)
        return self._forward[data]

    def compile(self, value, data=None):
        if self.default_data is not _Missed:
            return self._backward.get(value, self.default_data)
        if self.default_data_keep:
            return self._backward.get(value, value)
        return self._backward[value]


class Tuple(Base):
    serializers: tuple[Base, ...]
    iterate: bool

    def __init__(self, *serializers: Base, iterate: bool = False):
        self.serializers = serializers
        self.iterate = iterate

    def analyze(self, data):
        if self.iterate:
            return tuple(szr.analyze(dat) for szr, dat in zip(self.serializers, data, strict=True))
        return tuple(szr.analyze(data) for szr in self.serializers)

    def compile(self, value, data=None):
        # if self.iterate:
        return tuple(szr.compile(val, data) for szr, val in zip(tuple(self.serializers), value, strict=True))
        # return tuple(szr.compile(value, data) for szr in self.serializers)

    def get_keys(self) -> Iterator[str]:
        for szr in self.serializers:
            yield from szr.get_keys()


class StrSplit(Base):
    def __init__(self, separator: str | None = None):
        self.separator = separator

    def analyze(self, data):
        return data.split(self.separator)

    def compile(self, value, data=None):
        if self.separator is not None:
            return self.separator.join(value)
        return ''.join(value)


class NameTuple(Base):
    def __init__(self, *names: str, strict: bool = False):
        self.names = names
        self.strict = strict

    def analyze(self, data):
        return dict(zip(self.names, data, strict=self.strict))

    def compile(self, value, data=None):
        if self.strict and len(data) != len(self.names):
            raise ValueError()  # todo
        return tuple(data[name] for name in self.names)


def extract_unused(data: dict, keys, insert_unused=False, unused_key=Ellipsis):
    new_data = {key: val for key, val in data.items() if key in keys}
    if isinstance(data, factorydict):
        new_data = factorydict(data.default_factory, new_data)
    if insert_unused:
        unused = {key: val for key, val in data.items() if key not in keys}
        if unused:
            new_data[unused_key] = unused
    return new_data


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
        data = extract_unused(data, self.from_key, Ellipsis in self.from_key, Ellipsis)

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
        value = extract_unused(value, self.from_name, Ellipsis in self.from_name, Ellipsis)

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

    def __or__(self, other: 'WrapKeys'):
        return self.combine(other)


@frozen(init=False)
class FieldInfo:
    name: str | EllipsisType
    serializer: Base = None
    keys: tuple[str, ...] = None
    optimize_name: bool = True
    always_compile: bool = False
    compile_takes_value: bool = False

    def __init__(self,
                 name: str | EllipsisType = None,
                 serializer: Base | str | None | Literal[True] = None,
                 keys: tuple[str, ...] | Literal[True] | None = True,
                 optimize_name: bool = True,
                 always_compile: bool = False,
                 compile_takes_value: bool = False,
                 *,
                 additional_serializer: Base | None = None
                 ):
        if serializer is True:
            serializer = Key(name)
        elif isinstance(serializer, str):
            serializer = Key(serializer)
        if isinstance(serializer, Base):
            if keys is True:
                keys = tuple(serializer.get_keys())
                if not keys:
                    serializer = Key(name) >> serializer
                    keys = (name,)
            elif keys is None:
                keys = tuple(serializer.get_keys())
        if additional_serializer is not None:
            serializer = serializer >> additional_serializer
        if not isinstance(serializer, Base) or not isinstance(keys, tuple):
            raise TypeError()  # todo
        _setattr = partial(object.__setattr__, self)
        _setattr('name', name)
        _setattr('serializer', serializer)
        _setattr('keys', keys)
        _setattr('optimize_name', optimize_name)
        _setattr('always_compile', always_compile)
        _setattr('compile_takes_value', compile_takes_value)


class MultiField(Base):
    infos: tuple[FieldInfo, ...]
    from_key: dict[str, FieldInfo]
    from_name: dict[str, FieldInfo]
    force_default_names: dict[FieldInfo, None]  # ordered set
    always_compile: dict[FieldInfo, None]

    def __init__(self, *infos: FieldInfo):
        self.infos = infos
        self.from_key = {}
        self.from_name = {}
        self.force_default_names = {}
        self.always_compile = {}
        for info in self.infos:
            if info.name is not None:
                self.from_name[info.name] = info
            for key in info.keys:
                self.from_key[key] = info
            if not info.optimize_name:
                self.force_default_names[info] = None
            if info.always_compile:
                self.always_compile[info] = None

    def analyze(self, data: dict):
        data = extract_unused(data, self.from_key, Ellipsis in self.from_key, Ellipsis)

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
        value = extract_unused(value, self.from_name, Ellipsis in self.from_name, Ellipsis)

        if data is None:
            data = {}

        used_fields = dict(self.always_compile)  # ordered set
        for name in value:
            used_fields[self.from_name[name]] = None

        for info in used_fields:
            if info.serializer is None:
                continue
            if info.compile_takes_value:
                val = value
            else:
                val = value.get(info.name, None)
            info.serializer.compile(val, data)

        if Ellipsis in data:
            data.update(data.pop(Ellipsis))

        return data

    def combine(self, other: 'MultiField') -> 'MultiField':
        infos = tuple(info for info in self.infos if (
            (info.name is None or info.name not in other.from_name)
        ))  # if name presents in other, the info will be overriden.
        return MultiField(*infos, *other.infos)

    def __or__(self, other: 'MultiField'):
        return self.combine(other)

    def get_keys(self) -> Iterator[str]:
        for info in self.infos:
            yield from info.keys


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


class ToAttrs(Base):
    def __init__(self, klass: type[object], *slots: str):
        self.klass = klass
        has_dict = '__dict__' in dir(klass)
        if has_dict or not hasattr(klass, '__slots__'):
            raise TypeError()  # todo
        if not slots:
            self.slots = tuple(slot for slot in klass.__slots__ if slot != '__weakref__')
        else:
            self.slots = slots

    def analyze(self, data):
        return self.klass(*data)

    def compile(self, value, data=None):
        return tuple(getattr(value, name) for name in self.slots)


class ToEnum(Base):
    def __init__(self, klass: type[Enum]):
        self.klass = klass

    def analyze(self, data):
        return self.klass(data)

    def compile(self, value: Enum, data=None):
        return value.value


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


class SplitDict(Base):
    def __init__(self,
                 serializer: Base,
                 separator: str
                 ):
        self.serializer = serializer
        self.separator = separator

    def analyze(self, data: str):
        return pairs_to_dict(self.serializer.analyze(val) for val in data.split(self.separator))

    def compile(self, value, data=None):
        return self.separator.join(self.serializer.compile(val) for val in dict_to_pairs(value))


def MultiKey(*keys: str):
    return Tuple(*(Key(k) if isinstance(k, str) else k for k in keys))
