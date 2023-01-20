# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import typing as t

import jsonschema
import jsonschema.exceptions

from . import exceptions, loader

log = logging.getLogger(__name__)
config = loader.load_yaml()


def validate_schema():
    config_schema = loader.load_config_schema()
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError as error:
        raise exceptions.InvalidConfigurationError(
            f"{error.__class__.__name__}: {error.message}",
        ) from None
