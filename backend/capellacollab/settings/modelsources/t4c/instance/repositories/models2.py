# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models2 as t4c_models2,
)
from capellacollab.settings.modelsources.t4c.instance import (
    models2 as settings_t4c_models2,
)

from . import models


class SimpleT4CRepositoryWithIntegrations(core_pydantic.BaseModel):
    id: int
    name: str
    status: models.T4CRepositoryStatus | None = None
    instance: settings_t4c_models2.SimpleT4CInstance
    integrations: list[t4c_models2.SimpleT4CModelWithToolModel]
