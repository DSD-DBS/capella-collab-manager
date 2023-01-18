# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import typing as t

from jsonschema import exceptions, validate

from . import loader

log = logging.getLogger(__name__)

config = loader.load_yaml()


class InvalidConfigurationError(Exception):
    pass


def validate_schema():
    config_schema = loader.load_config_schema()
    try:
        validate(config, config_schema)
    except exceptions.ValidationError as error:
        raise InvalidConfigurationError(
            f"{error.__class__.__name__}: {error.message}",
        ) from None
