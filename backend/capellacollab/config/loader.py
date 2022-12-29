# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import pathlib

import appdirs
import yaml

log = logging.getLogger(__name__)

locations: list[pathlib.Path] = [
    pathlib.Path(__file__).parents[2] / "config",
    pathlib.Path(appdirs.user_config_dir("capellacollab", "db")),
    pathlib.Path("/etc/capellacollab"),
]

fallback_locations: list[pathlib.Path] = [
    pathlib.Path(__file__).parents[2] / "config" / "config_template.yaml",
]


def load_yaml() -> dict:
    config_locations = list(map(lambda loc: loc / "config.yaml", locations))
    config_fallback_locations = fallback_locations

    log.debug("Searching for configuration files...")
    for loc in config_locations:
        if loc.exists():
            log.info("Loading configuration file at location %s", str(loc))
            return yaml.safe_load(loc.open())
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

    return {}


def load_config_schema() -> dict:
    json_schema_locations = list(
        map(lambda loc: loc / "config_schema.json", locations)
    )
    for loc in json_schema_locations:
        if loc.exists():
            log.info(
                "Loading configuration schema file at location %s", str(loc)
            )
            with open(loc, encoding="utf-8") as json_schema:
                return json.load(json_schema)
        else:
            log.debug(
                "Didn't find a configuration schema file at location %s",
                str(loc),
            )
    return {}
