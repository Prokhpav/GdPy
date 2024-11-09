import inspect
from typing import Callable, Iterable


def nothing(*args):
    if not args:
        return None
    if len(args) == 1:
        return args[0]
    return args


def pairs_to_dict[T](elems: Iterable[T]) -> dict[T, T]:
    elems_iter = iter(elems)
    return dict(zip(elems_iter, elems_iter, strict=True))


def dict_to_pairs(d):
    return (x for pair in d.items() for x in pair)


def map_default(target_func, map_func):
    """ for all default values name=default in target_func replaces default to map_func(name, default) """
    pos_defaults = target_func.__defaults__
    kw_defaults = target_func.__kwdefaults__
    pos_defaults = pos_defaults if pos_defaults is not None else ()
    kw_defaults = kw_defaults if kw_defaults is not None else {}
    pos_default_names = target_func.__code__.co_varnames[-len(pos_defaults):target_func.__code__.co_argcount]
    pos_defaults = tuple(map_func(name, default) for name, default in zip(pos_default_names, pos_defaults))
    kw_defaults = {name: map_func(name, default) for name, default in kw_defaults.items()}
    target_func.__defaults__ = pos_defaults
    target_func.__kwdefaults__ = kw_defaults


def args_to_kwargs(func, args, kwargs, remove_self=True):
    if not isinstance(func, inspect.Signature):
        func = inspect.signature(func)
    if remove_self:
        func = func.replace(parameters=[p for name, p in func.parameters.items() if name != 'self'])
    args = func.bind_partial(*args, **kwargs)
    return args.arguments


class factorydict[KT, VT](dict[KT, VT]):
    """ Same as defaultdict, but default_factory takes key as argument """
    __slots__ = ('default_factory',)

    def __init__(self, default_factory: Callable[[KT], VT] | None = None, *args, **kwargs):
        self.default_factory = default_factory
        super().__init__(*args, **kwargs)

    def __missing__(self, key: KT) -> VT:
        if self.default_factory is None:
            raise KeyError(key)
        return self.default_factory(key)

    def copy(self):
        return factorydict(self.default_factory, self)


class Factory[T]:
    __slots__ = ('factory',)

    def __init__(self, factory: Callable[[], T]):
        self.factory = factory

    @classmethod
    def unwrap(cls, value: 'Factory[T] | T') -> T:
        if isinstance(value, cls):
            return value.factory()
        return value

    def __repr__(self):
        return f'Factory({self.factory!r})'
