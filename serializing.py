from attrs import define, field
from typing import *
from collections.abc import Iterable, Iterator, Callable
import recognizing

SzrCallable = Callable[[Any], Any]

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


class FieldBase:
    """
    Almost like serializer, but analyser also uses second argument mutation rather returning.
    """

    def analyse(self, data: dict, value: dict):
        """ Extract information from data and add it to value """
        raise NotImplementedError()

    def compile(self, value: dict, data: dict):
        """ Extract information from value and add it to data """
        raise NotImplementedError()

    def get_keys(self) -> Iterator[str]:
        yield from ()


class DictFields(Base):
    """
    Applies each field to data, returns the resulting dict value.
    """

    def __init__(self, fields: tuple[FieldBase, ...]):
        self.fields = fields

    def analyze(self, data: dict):
        value = {}
        for field_ in self.fields:
            field_.analyse(data, value)
        return value

    def compile(self, value, data=None):
        if data is None:
            data = {}
        for field_ in self.fields:
            field_.compile(value, data)
        return data


@define
class FieldCommon(FieldBase):
    """
    This field can be optimized in DictFieldsOptimized - if there are no keys of
        the field.get_keys() in the data, the field's value will not be calculated.
    value[name] = serializer.analyse(data)
    """
    name: str
    serializer: Base

    def analyse(self, data: dict, value: dict):
        val = self.serializer.analyze(data)
        if val is not None:
            value[self.name] = val

    def compile(self, value: dict, data: dict):
        val = value.get(self.name, None)
        self.serializer.compile(val, data)

    def get_keys(self) -> Iterator[str]:
        yield from self.serializer.get_keys()


class DictFieldsOptimized(Base):
    fields: tuple[FieldBase, ...]
    unused: FieldBase | None
    unoptimized_fields: tuple[FieldBase, ...]
    optimized_fields: tuple[FieldCommon, ...]
    from_key: dict[str, FieldCommon]
    from_name: dict[str, FieldCommon]

    def __init__(self,
                 fields: tuple[FieldBase, ...],
                 unused: FieldBase | None = None
                 ):
        self.fields = fields
        self.unused = unused
        self.unoptimized_fields = tuple(field_ for field_ in fields if not isinstance(field_, FieldCommon))
        self.optimized_fields = tuple(field_ for field_ in fields if isinstance(field_, FieldCommon))
        self.from_key: dict[str, FieldCommon] = {}
        self.from_name = {}
        for field_ in self.optimized_fields:
            for key in field_.get_keys():
                self.from_key[key] = field_
            self.from_name[field_.name] = field_

    def analyze(self, data: dict):
        value = {}
        for field_ in self.unoptimized_fields:
            field_.analyse(data, value)

        unused_keys = {}
        used_field_names = {}  # ordered set
        for key, val in data.items():
            if key in self.from_key:
                used_field_names[self.from_key[key].name] = None
            elif self.unused is not None:
                unused_keys[key] = val

        for name in used_field_names:
            value[name] = self.from_name[name].serializer.analyze(data)

        if unused_keys and self.unused is not None:
            self.unused.analyse(unused_keys, value)

        return value

    def compile(self, value: dict, data: dict = None):
        if data is None:
            data = {}

        unused_keys = {}
        if self.unused is not None:
            self.unused.compile(value, unused_keys)

        for name, val in value.items():
            if name in self.from_key:
                self.from_name[name].serializer.compile(val, data)

        for field_ in self.unoptimized_fields:
            field_.compile(value, data)

        return data

    def get_keys(self) -> Iterator[str]:
        for field_ in self.fields:
            yield from field_.get_keys()


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
