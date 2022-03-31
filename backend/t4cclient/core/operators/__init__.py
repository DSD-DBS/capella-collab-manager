from __future__ import annotations

from importlib import metadata

from t4cclient.config import config
from t4cclient.core.operators.abc import Operator

try:
    OPERATOR = next(
        i
        for i in metadata.entry_points()["capellacollab.operators"]
        if i.name == config["operators"]["operator"]
    ).load()()

except StopIteration:
    raise KeyError(f"Unknown operator " + config["operators"]["operator"]) from None
