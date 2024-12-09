# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import pathlib

import appdirs
import yaml

from . import exceptions

log = logging.getLogger(__name__)
CONFIG_FILE_NAME = "config.yaml"

config_locations: list[pathlib.Path] = [
    pathlib.Path(__file__).parents[0] / CONFIG_FILE_NAME,
    pathlib.Path(__file__).parents[3] / "config" / CONFIG_FILE_NAME,
    pathlib.Path(appdirs.user_config_dir("capellacollab", "db"))
    / CONFIG_FILE_NAME,
    pathlib.Path("/etc/capellacollab") / CONFIG_FILE_NAME,
]


# https://gist.github.com/pypt/94d747fe5180851196eb?permalink_comment_id=4015118#gistcomment-4015118
class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise exceptions.InvalidConfigurationError(
                    f"Duplicate key {key!r} found in configuration."
                )
            mapping.add(key)
        return super().construct_mapping(node, deep)


def does_config_exist() -> bool:
    for loc in config_locations:
        if loc.exists():
            return True

    return False


def load_yaml() -> dict:
    log.debug("Searching for configuration files...")
    for loc in config_locations:
        if loc.exists():
            log.info(
                "Loading configuration file at location %s",
                str(loc.absolute()),
            )
            with loc.open(encoding="utf-8") as f:
                return yaml.load(f, UniqueKeyLoader)
        else:
            log.debug(
                "Didn't find a configuration file at location %s", str(loc)
            )

    raise FileNotFoundError("config.yaml")
