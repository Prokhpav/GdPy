from typing import Any

from tools.funcs import args_to_kwargs


__all__ = ('Maker',)


class _MakerWrapperItem[T]:
    def __init__(self, maker: 'Maker[T]'):
        self.maker = maker
        self.default_kwargs = {}

    @property
    def setup(self) -> type[T]:
        def setup(*args, **kwargs):
            self.default_kwargs = args_to_kwargs(self.maker.klass.__init__, args, kwargs)

        return setup

    def __call__(self, *args, **kwargs) -> T:
        kwargs = self.maker.args_to_kwargs(args, kwargs)
        kwargs = self.maker.default_kwargs | self.default_kwargs | kwargs
        return self.maker.klass(**kwargs)


class Maker[T]:
    def __init__(self, klass: type[T]):
        self.klass = klass
        self._items: dict[Any, _MakerWrapperItem[T]] = {}
        self.default_kwargs = {}

    def args_to_kwargs(self, args, kwargs):
        x = args_to_kwargs(self.klass.__init__, args, kwargs)
        if 'self' in x:
            pass
        return x

    @property
    def setup(self) -> type[T]:
        def setup(*args, **kwargs):
            self.default_kwargs = self.args_to_kwargs(args, kwargs)

        return setup

    def __call__(self, key) -> _MakerWrapperItem[T]:
        if key not in self._items:
            self._items[key] = _MakerWrapperItem(self)
        return self._items[key]

    def __getitem__(self, key) -> type[T]:
        return self._items[key]
