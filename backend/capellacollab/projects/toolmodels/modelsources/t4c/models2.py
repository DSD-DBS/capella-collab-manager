# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.toolmodels import models as toolmodels_models


class SimpleT4CModelWithToolModel(core_pydantic.BaseModel):
    id: int
    name: str
    model: toolmodels_models.SimpleToolModel
