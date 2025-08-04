#!/usr/bin/env -S python3 -O
# -*- coding = utf-8 -*-
"""bots base classes.
"""

__version__ = '0.0.1'
__all__ = [
    'BotAdapterProtocol',
    'BotAdapter',
    'Adaptee',
]

from abc import ABC, abstractmethod
from typing import (
    Optional,
    Protocol, runtime_checkable,
)

NoneType: type = type(None)


@runtime_checkable
class BotAdapterProtocol(Protocol):
    """Abstract BotAdapter protocol."""
    @abstractmethod
    def send_message(self, msg, /, *args, **kwargs):
        """Send massage using this bot."""


class Adaptee:
    """Adaptee descriptor class."""
    def __init__(self, t: Optional[type] = NoneType, /):
        self.cls = t if isinstance(t, type) else type(t)

    @property
    def has_type(self):
        return (self.cls is not NoneType)

    def __set_name__(self, owner, name, /):
        self.owner = owner
        self.public_name = name
        
    @property
    def private_name(self):
        return '__' + self.public_name + '_instance'

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj, value, /):
        if self.has_type and not isinstance(value, self.cls):
            raise TypeError(f'{self.public_name} value {value!r} '
                            f'must be an instance of type {self.cls!r}.')
        setattr(obj, self.private_name, value)


class _AdapterBase(ABC):
    """Base Adapter logic class."""
    adaptee = Adaptee()
        
    def __init__(self, adaptee: object):
        self.adaptee = adaptee

    def __repr__(self):
        return self.__class__.__qualname__ + f'({self.adaptee!r})'

    def __getattr__(self, name):
        return getattr(self.adaptee, name)


class BotAdapter(_AdapterBase):
    pass


## MAIN ENTRY POINT
def main():
    pass


if __name__ == '__main__':
    main()
