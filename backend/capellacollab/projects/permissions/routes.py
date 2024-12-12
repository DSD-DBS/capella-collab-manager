# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from . import models

router = fastapi.APIRouter()


@router.get("")
def get_available_project_permissions():
    return models.ProjectUserScopes.model_json_schema()
