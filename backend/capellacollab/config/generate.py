# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import yaml

from . import models

log = logging.getLogger(__name__)


def write_config() -> None:
    """Write the default configuration to a config file."""

    config_path = (
        pathlib.Path(__file__).parent.parent.parent / "config" / "config.yaml"
    )

    config_path.parent.mkdir(parents=True, exist_ok=True)

    _ansi_red = "\x1b[31;40m"
    _ansi_reset = "\x1b[0m"
    log.warning(
        "%sNo configuration file found. Generating default configuration at %s%s",
        _ansi_red,
        str(config_path.absolute()),
        _ansi_reset,
    )

    with config_path.open("w") as yaml_file:
        yaml.dump(
            models.AppConfig().model_dump(by_alias=True),
            yaml_file,
            sort_keys=False,
        )
