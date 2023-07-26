# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pydantic

from capellacollab.projects.toolmodels.backups.runs import (
    models as pipeline_run_models,
)
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)


class StatusResponse(pydantic.BaseModel):
    guacamole: bool
    database: bool
    operator: bool


class ToolmodelStatus(pydantic.BaseModel):
    project_slug: str
    model_slug: str

    warnings: list[str]
    primary_git_repository_status: git_models.GitModelStatus
    pipeline_status: pipeline_run_models.PipelineRunStatus | None
    model_badge_status: git_models.ModelArtifactStatus
    diagram_cache_status: git_models.ModelArtifactStatus


class ProjectStatus(pydantic.BaseModel):
    project_slug: str
    warnings: list[str]
