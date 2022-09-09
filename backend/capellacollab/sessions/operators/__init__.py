# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from importlib import metadata

from capellacollab.config import config

try:
    OPERATOR = next(
        i
        for i in metadata.entry_points()["capellacollab.operators"]
        if i.name == config["operators"]["operator"]
    ).load()()

except StopIteration:
    raise KeyError(
        f"Unknown operator " + config["operators"]["operator"]
    ) from None
