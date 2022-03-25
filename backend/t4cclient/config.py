import abc
import logging
import os
import typing as t

import yaml

_KT = t.TypeVar("_KT")

log = logging.getLogger(__name__)

class ConfigDict(dict):
    path = []

    def __init__(self, path: list):
        self.path = path

    def __getitem__(self, __k: str) -> "ConfigDict" | "ConfigList" | float | int | str:
        # Read environment variable
        env_key = "_".join([i.upper() for i in self.path + [__k]])
        env_value = os.environ.get(env_key)

        # Read yaml
        yaml_key = ".".join([i for i in self.path + [__k]])
        yaml_value = self.get(__k)
        value = yaml_value

        # TODO: Implement default values / fallback

        if yaml_value and env_value: 
            log.warning("Clashing environment variables. Found environment variable %s and yaml variable %s", env_key, env_value)
            log.warning("Will use the yaml value, because it has a higher priority.")

        value = yaml_value or env_value

        if isinstance(value, str | int | float):
            return value 
        elif isinstance(value, dict): 
            return ConfigDict(self.path + [__k], value)
        elif isinstance(value, list):
            return ConfigList(self.path + [__k], value)
        raise TypeError(f"Unspported type of value {type(value)}") 
        

class ConfigList(list): 
    def __getitem__(self, __i: t.SupportsIndex) -> "ConfigDict" | "ConfigList" | float | int | str: 
        