# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import os
import pathlib
import typing as t

from jsonschema import validate

from . import loader

log = logging.getLogger(__name__)

config = loader.load_yaml()
config_schema = loader.load_config_schema()

validate(config, config_schema)
