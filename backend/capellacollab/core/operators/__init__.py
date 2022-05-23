# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
from importlib import metadata

# 1st party:
from capellacollab.config import config
from capellacollab.core.operators.abc import Operator

try:
    OPERATOR = next(
        i
        for i in metadata.entry_points()["capellacollab.operators"]
        if i.name == config["operators"]["operator"]
    ).load()()

except StopIteration:
    raise KeyError(f"Unknown operator " + config["operators"]["operator"]) from None
