# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
import logging
import os
import typing as t

# local:
from . import loader

log = logging.getLogger(__name__)


class ConfigDict(dict):
    path: list[str | int]

    def __init__(self, value: dict, path: list = []) -> None:
        super().__init__(value)
        self.path = path

    def __getitem__(self, __k: str) -> "ConfigDict" | "ConfigList" | float | int | str:
        # Read environment variable
        env_key = "_".join([i.upper() for i in self.path + [__k]])
        env_value = os.environ.get(env_key, "")

        # Read dict
        yaml_key = ".".join([i for i in self.path + [__k]])
        yaml_value = super().get(__k)
        value = yaml_value

        # TODO: Implement default values / fallback

        if yaml_value and env_value:
            log.warning(
                "Clashing environment variables. Found environment variable %s and yaml variable %s",
                env_key,
                yaml_key,
            )
            log.warning("Will use the yaml value, because it has a higher priority.")

        value = yaml_value or env_value

        if not value:
            return ConfigDict({}, self.path + [__k])
        if isinstance(value, (str, int, float)):
            return value
        elif isinstance(value, dict):
            return ConfigDict(value, self.path + [__k])
        elif isinstance(value, list):
            return ConfigList(value, self.path + [__k])

        raise TypeError(f"Unspported type of value {type(value)}")

    def _immutable(self, *args, **kws):
        raise TypeError("ConfigDict is immutable")

    def _unsupported(self, *args, **kws):
        raise NotImplementedError("This function is not supported")

    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    popitem = _immutable
    update = _immutable
    clear = _immutable
    setdefault = _immutable

    __lt__ = _unsupported
    __le__ = _unsupported
    __ne__ = _unsupported
    __eq__ = _unsupported
    __gt__ = _unsupported
    __ge__ = _unsupported


class ConfigList(list):
    path: list[str | int]

    def __init__(self, value: dict, path: list = []) -> None:
        super().__init__(value)
        self.path = path

    def __getitem__(
        self, __i: t.SupportsIndex
    ) -> "ConfigDict" | "ConfigList" | float | int | str:
        # Read dict
        value = super().__getitem__(__i)

        if isinstance(value, (str, int, float)):
            return value
        elif isinstance(value, dict):
            return ConfigDict(value, self.path + [f"[{__i}]"])
        elif isinstance(value, list):
            return ConfigList(value, self.path + [f"[{__i}]"])
        raise TypeError(f"Unspported type of value {type(value)}")

    def _immutable(self, *args, **kws):
        raise TypeError("ConfigList is immutable")

    def _unsupported(self, *args, **kws):
        raise NotImplementedError("This function is not supported")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    append = _immutable
    insert = _immutable
    extend = _immutable
    pop = _immutable
    remove = _immutable
    sort = _immutable

    __lt__ = _unsupported
    __le__ = _unsupported
    __ne__ = _unsupported
    __eq__ = _unsupported
    __gt__ = _unsupported
    __ge__ = _unsupported
    __add__ = _unsupported
    __mul__ = _unsupported
    __rmul__ = _unsupported
    __iadd__ = _unsupported
    __imul__ = _unsupported


config_tmp = loader.load_yaml()
if config_tmp:
    config = ConfigDict(config_tmp)
else:
    config = ConfigDict({})
