from typing import ClassVar, Self

class NamedSingleton:
    """
    Create constants like Ellipsis

    Creating:
        class Missed(NamedSingleton): ...
        Missed = Missed()

    Usage:
        def foo(x: int | type(Missed)):
            if x is Missed:
                return factory()
            return x

        foo({}.get('bar', Missed))

        print(Missed)  # >>> Missed
    """

    __instance__: ClassVar[Self] = None

    def __new__(cls):
        return cls.__instance__

    def __init_subclass__(cls, **kwargs):
        cls.__instance__ = object.__new__(cls)
        super().__init_subclass__(**kwargs)

    def __repr__(self):
        return self.__class__.__name__

class Default(NamedSingleton):
    """ Use as default value in function when you can't use None """

Default = Default()

class Missed(NamedSingleton):
    """ Some data is not found. Example: dict().get(key, Missed) """

Missed = Missed()
