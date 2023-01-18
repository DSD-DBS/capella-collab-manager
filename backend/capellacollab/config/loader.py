# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import pathlib

import appdirs
import yaml

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


def load_yaml() -> dict:
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

    raise FileNotFoundError("config.yaml")


def load_config_schema() -> dict:
    return json.loads(
        (pathlib.Path(__file__).parents[0] / "config_schema.json").read_bytes()
    )
