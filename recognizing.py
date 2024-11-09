from collections.abc import Callable
from typing import Any
from python.attrs_wrap import attrs_init_only

_Missed = object()


def _as_sequence(r) -> tuple:
    if isinstance(r, Sequence):
        return r.recognizers
    return (r,)


class Base:
    """
    One-way conversion of data to a recognized characteristic.
    Can create Sequence of recognizers using `>>`: foo >> bar >> baz
    """

    def __call__(self, data):
        raise NotImplementedError()

    def __rshift__(self, other):
        return Sequence(_as_sequence(self) + _as_sequence(other))


class Sequence(Base):
    """
    Sequentially applies recognizers to data. The next one operates on the result of the previous one.
    """

    def __init__(self, recognizers: tuple[Base, ...]):
        self.recognizers = recognizers

    def __call__(self, data):
        for rzr in self.recognizers:
            data = rzr(data)
        return data


class Func(Base):
    """
    Wrapper around function.
    """

    def __init__(self, func: Callable[[Any], Any]):
        self.func = func

    def __call__(self, data):
        return self.func(data)


class Key(Base):
    """
    Tries to get the value of a key from the data.
    If there is no key in the data, raises a KeyError or returns a default value.
    If a converter is set, it will convert the found value.
    """

    def __init__(self,
                 key: str,
                 converter: Callable[[Any], Any] | None = None,
                 default: Any = _Missed
                 ):
        self.key = key
        self.converter = converter
        self.default = default

    def __call__(self, data):
        if self.key not in data:
            if self.default is not _Missed:
                return self.default
            raise KeyError(self.key)
        if self.converter is None:
            return data[self.key]
        return self.converter(data[self.key])


class Tuple(Base):
    """
    Applies each recognizer to the data and returns a tuple of results.
    """

    def __init__(self, *recognizers: Base):
        self.recognizers = recognizers

    def __call__(self, data):
        return tuple(rzr(data) for rzr in self.recognizers)


@attrs_init_only
class Nested(Base):
    """
    Applies the recognizer to the data and calls the `convert` method.
    If it returns another recognizer, it applies that to the data and returns the result.
    The `convert` method can be overridden in subclasses, but here it does nothing.
    """
    recognizer: Base | Callable[[Any], Any]

    def convert(self, value):
        return value

    def __call__(self, data):
        result = self.convert(self.recognizer(data))
        if isinstance(result, Base):
            return result(data)
        return result


@attrs_init_only
class Map(Nested):
    """
    Converts the result using mapping. If there is no such key, it uses `...` as a default key if such a key exists.
    For example, calling this:
        return Map(Key('foo'), {
            1: Key('bar'),
            ...: 0
        })(data)
    Is equivalent to:
        key = data['foo']
        if key == 1:
            return data['bar']
        return 0
    """
    mapping: dict

    def convert(self, value):
        if value in self.mapping:
            return self.mapping[value]
        if ... in self.mapping:
            return self.mapping[...]
        raise KeyError(value)



