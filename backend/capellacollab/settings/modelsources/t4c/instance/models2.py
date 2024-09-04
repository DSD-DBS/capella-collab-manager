# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.core import pydantic as core_pydantic
from capellacollab.tools import models as tools_models


class SimpleT4CInstance(core_pydantic.BaseModel):
    id: int
    name: str
    version: tools_models.SimpleToolVersion
    is_archived: bool
