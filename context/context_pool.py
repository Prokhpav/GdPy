import functools
import inspect
from typing import TYPE_CHECKING

from attrs import define, field
from types import EllipsisType

from contextlib import contextmanager
from context.context_prop import ContextNode, ContextProperty

@define
class ContextPoolProperty[T](ContextProperty):
    name: str = field(init=False)
    pool: 'ContextPool' = field(init=False)

    def __prop_init__(self, name: str, pool: 'ContextPool'):
        self.name = name
        self.pool = pool

    def get(self) -> T:
        if not self.stack:
            raise RuntimeError(f"ContextPoolProperty {self.name!r} no value")
        return self.stack[-1]()

    @contextmanager
    def add(self, node: ContextNode[T]):
        self.stack.append(node)
        try:
            node.__prop_init__(self, len(self.stack) - 1)
            with self.pool.node_added(self.name), node:
                yield
        finally:
            self.stack.pop()

@define
class ContextPool:
    _props: dict[str, ContextPoolProperty] = field(init=False, factory=dict)
    nondefaults: set[str] = field(init=False, factory=set)

    def __getitem__(self, name: str) -> ContextPoolProperty:
        return self._props[name]

    @contextmanager
    def node_added(self, name: str):
        if name in self.nondefaults:
            yield
            return
        self.nondefaults.add(name)
        try:
            yield
        finally:
            self.nondefaults.remove(name)

    def register(self, *names: str, **props: ContextPoolProperty):
        for name in names:
            if name in props:
                raise TypeError(f'{ContextPool.register.__name__} got multiple values for {name!r}')
            props[name] = ContextPoolProperty()
        for name, prop in props.items():
            self._props[name] = prop
            prop.__prop_init__(name, self)

    def decorate_func(self, *same_name: str, __register__: bool = False, **other_name: str | EllipsisType):
        """
        Attaches ContextPoolProperty as default factory to each given argument.
        :param same_name: get prop with the same name from pool
        :param other_name: get prop with this name from pool.
        :param __register__: if true, register all unknown prop names

        context_pool.register('a', 'b', 'car')

        @context_pool.decorate_func('a', b=..., c='car')
        def func(a=0, b=0, c=0, d=4):
            print((a, b, c, d))

        with context_pool['car'].add_value(3):
            func(1, b=2)  # >> (1, 2, 3, 4)
        """

        props: dict[str, str] = {}
        for name in same_name:
            props[name] = name
            if name in other_name:
                TypeError(f'{self.decorate_func.__name__} got multiple values for argument {name!r}')
        for name, prop_name in other_name.items():
            props[name] = name if prop_name is Ellipsis else prop_name

        if __register__:
            self.register(*(name for name in props.values() if name not in self._props))
        else:
            for name in props.values():
                if name not in self._props:
                    raise KeyError(f"Can't get prop for {name!r}")

        def decorator[T](func: T) -> T:
            if TYPE_CHECKING:
                return func
            argnames = inspect.getfullargspec(func).args

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                args_kwargs = dict(zip(argnames, args))
                for arg_name in args_kwargs:
                    if arg_name in kwargs:
                        raise TypeError(f'{func.__name__} got multiple values for argument {arg_name!r}')
                kwargs.update(args_kwargs)
                kwargs.update({name: self._props[props[name]].get() for name in props - kwargs.keys()})
                return func(**kwargs)

            return wrapper

        return decorator

if __name__ == '__main__':
    @(lambda _: _())
    def _():
        context_pool = ContextPool()
        # context_pool.register('a', 'b', 'car')

        @context_pool.decorate_func('a', b=..., c='car', __register__=True)
        def func(a, b, c):
            print((a, b, c))

        with (
            context_pool['a'].add_value(1),
            context_pool['b'].add_value(2),
            context_pool['car'].add_value(3)
        ):
            func(-1)  # >> (-1, 2, 3)
