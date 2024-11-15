# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pydantic

from capellacollab.core import pydantic as core_pydantic


class IdleState(core_pydantic.BaseModel):
    available: bool
    idle_for_minutes: int | None = pydantic.Field(
        default=None,
        description="The number of minutes the session has been idle. Value is -1 if the session has never been connected to.",
    )
    terminate_after_minutes: int
    unavailable_reason: str | None = pydantic.Field(default=None)
