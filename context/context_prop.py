from typing import Generic, TypeVar, Callable
from attrs import define, field
from contextlib import contextmanager

T = TypeVar("T")

class ContextNode(Generic[T]):
    def __prop_init__(self, prop: 'ContextProperty[T]', index: int):
        pass

    def __call__(self) -> T:
        raise NotImplementedError()

    def __enter__(self):
        pass

    def __exit__(self, _, err, __):
        pass

@define
class ContextNodeValue(ContextNode[T]):
    value: T

    def __call__(self) -> T:
        return self.value

@define
class ContextNodeFunc(ContextNode[T]):
    func: Callable[[], T]

    def __call__(self):
        return self.func()

@define
class ContextNodeFuncEdit(ContextNode[T]):
    func: Callable[[T], T] = field()
    prop: 'ContextProperty[T]' = field(init=False)
    index: int = field(init=False)

    def __prop_init__(self, prop: 'ContextProperty[T]', index: int):
        self.prop = prop
        self.index = index
        if self.index == 0:
            raise TypeError("Can't edit non-existing value")

    def __call__(self):
        value = self.prop.stack[self.index-1]()
        return self.func(value)

@define
class ContextProperty(Generic[T]):
    """
    prop = ContextProperty()

    with prop.add_value(42):
        print(prop.get())  # -> 42
        with prop.add_func_edit(lambda x: x+1):
            print(prop.get())  # -> 43
    """

    stack: list[ContextNode[T]] = field(init=False, factory=list)

    def get(self) -> T:
        if not self.stack:
            raise RuntimeError("ContextProperty no value")
        return self.stack[-1]()

    @contextmanager
    def add(self, node: ContextNode[T]):
        self.stack.append(node)
        try:
            node.__prop_init__(self, len(self.stack)-1)
            with node:
                yield
        finally:
            self.stack.pop()

    def add_value(self, value: T):
        return self.add(ContextNodeValue(value))

    def add_func(self, func: Callable[[], T]):
        return self.add(ContextNodeFunc(func))

    def add_func_edit(self, func: Callable[[T], T]):
        return self.add(ContextNodeFuncEdit(func))
