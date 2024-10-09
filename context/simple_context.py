from contextlib import contextmanager
import abc

class SimpleContext(abc.ABC):
    """ simulates contextmanager for a class with __context__ method
    @contextmanager decorator is necessary

    class FooCls(SimpleContext):
        @contextmanager
        def __context__(cls):
            print('enter')
            try:
                yield
            finally:
                print('exit')

    foo = FooCls()

    with foo.__context__():
        ...
    with foo:  # the same effect
        ...
    """
    __global_context_stack = []

    @contextmanager
    def __context__(self):
        raise NotImplementedError()
        yield

    def __enter__(self):
        manager = self.__context__()
        value = manager.__enter__()
        SimpleContext.__global_context_stack.append(manager)
        return value

    def __exit__(self, exc_type, exc_val, exc_tb):
        manager = SimpleContext.__global_context_stack.pop()
        return manager.__exit__(exc_type, exc_val, exc_tb)

