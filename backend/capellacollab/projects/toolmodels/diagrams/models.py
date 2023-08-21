# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import datetime

import pydantic

from capellacollab.core import pydantic as core_pydantic


class DiagramMetadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str
    uuid: str
    success: bool


class DiagramCacheMetadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    diagrams: list[DiagramMetadata]
    last_updated: datetime.datetime

    _validate_last_updated = pydantic.validator(
        "last_updated", allow_reuse=True
    )(core_pydantic.datetime_serializer)
