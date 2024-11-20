from contextlib import contextmanager
from .simple_context import SimpleContext
from typing import TypeVar, Type

T = TypeVar("T", bound="Contextable")

_Missed = object()


class Contextable(SimpleContext):
    _context_stack: list = None

    def __init_subclass__(cls, **kwargs):
        cls._context_stack = []
        super().__init_subclass__(**kwargs)

    @contextmanager
    def __context__(self):
        self.__class__._context_stack.append(self)
        try:
            yield self
        finally:
            assert self.__class__._context_stack.pop() is self

    @classmethod
    def C(cls: Type[T], default: T | None = _Missed) -> T | None:
        """ Current instance in context """
        if cls._context_stack:
            return cls._context_stack[-1]
        if default is _Missed:
            raise RuntimeError(f'{cls.__name__}: no context')
        return default
