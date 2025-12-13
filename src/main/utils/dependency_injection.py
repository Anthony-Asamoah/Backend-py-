from typing import Callable

from django.core.exceptions import ImproperlyConfigured


class MethodsContainer:
    def __init__(self):
        self.container = {}

    def register(self, func: Callable, *args, **kwargs) -> None:
        self.container[func.__name__] = dict(
            func=func, args=args, kwargs=kwargs
        )

    def unpack(self):
        return [(_['func'], _['args'], _['kwargs']) for _ in self.container.values()]


class VarContainer:
    def __init__(self):
        self.container = {}

    def register(self, var, name: str = None):
        key = var.__name__ if name is None else name
        self.container[key] = var

    def get(self, name: str):
        var = self.container.get(name)
        if not var: raise ImproperlyConfigured(f"{name} is not registered")
        return var
