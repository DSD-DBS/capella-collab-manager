# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import pathlib

import appdirs
import yaml

from . import exceptions

log = logging.getLogger(__name__)

config_locations: list[pathlib.Path] = [
    pathlib.Path(__file__).parents[2] / "config" / "config.yaml",
    pathlib.Path(appdirs.user_config_dir("capellacollab", "db"))
    / "config.yaml",
    pathlib.Path("/etc/capellacollab") / "config.yaml",
]

config_fallback_locations: list[pathlib.Path] = [
    pathlib.Path(__file__).parents[2] / "config" / "config_template.yaml",
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


def load_yaml() -> dict:
    log.debug("Searching for configuration files...")
    for loc in config_locations:
        if loc.exists():
            log.info("Loading configuration file at location %s", str(loc))
            return yaml.load(loc.open(), UniqueKeyLoader)
        else:
            log.debug(
                "Didn't find a configuration file at location %s", str(loc)
            )

    for loc in config_fallback_locations:
        if loc.exists():
            log.warning(
                "Loading fallback configuration file at location %s", str(loc)
            )
            return yaml.safe_load(loc.open())

    raise FileNotFoundError("config.yaml")


def load_config_schema() -> dict:
    return yaml.safe_load(
        (pathlib.Path(__file__).parents[0] / "config_schema.yaml").read_bytes()
    )
