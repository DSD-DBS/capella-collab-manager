# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import pathlib

import appdirs
import yaml

log = logging.getLogger(__name__)

locations: list[pathlib.Path] = [
    pathlib.Path(__file__).parents[2] / "config" / "config.yaml",
    pathlib.Path(appdirs.user_config_dir("capellacollab", "db")) / "config.yaml",
    pathlib.Path("/etc/capellacollab/config.yaml"),
]


def load_yaml() -> None | dict:
    log.debug("Searching for configuration files...")
    for l in locations:
        if l.exists():
            log.info("Found configuration file at location %s", str(l))
            return yaml.safe_load(l.open())
        else:
            log.debug("Didn't find a configuration file at location %s", str(l))

    return None
