# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

if t.TYPE_CHECKING:
    from . import models


def resolve_tool_ports(ports: "models.SessionPorts") -> dict[str, int]:
    model = ports.model_dump()
    additional = model["additional"]
    del model["additional"]

    return model | additional
