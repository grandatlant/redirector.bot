#!/usr/bin/env -S python3 -O
# -*- coding = utf-8 -*-
"""bots base classes.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class BotAdapter(Protocol):
    pass
