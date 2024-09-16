# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime

import pydantic

from capellacollab.core import pydantic as core_pydantic


class DiagramMetadata(core_pydantic.BaseModel):
    name: str
    uuid: str
    success: bool


class DiagramCacheMetadata(core_pydantic.BaseModel):
    diagrams: list[DiagramMetadata]
    last_updated: datetime.datetime
    job_id: str | None = None

    _validate_last_updated = pydantic.field_serializer("last_updated")(
        core_pydantic.datetime_serializer
    )
