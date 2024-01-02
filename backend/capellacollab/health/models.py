# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import typing as t

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
    toolmodel_slug: str = pydantic.Field(alias="model_slug")

    warnings: list[str]
    primary_git_repository_status: git_models.GitModelStatus
    pipeline_status: pipeline_run_models.PipelineRunStatus | None = None
    toolmodel_badge_status: git_models.ModelArtifactStatus = pydantic.Field(
        alias="model_badge_status"
    )
    diagram_cache_status: git_models.ModelArtifactStatus


class ProjectStatus(pydantic.BaseModel):
    project_slug: str
    warnings: list[str]


class ToolModelStatusTasks(t.TypedDict):
    primary_git_repository_status: asyncio.Task[git_models.GitModelStatus]
    model_badge_status: asyncio.Task[git_models.ModelArtifactStatus]
    diagram_cache_status: asyncio.Task[git_models.ModelArtifactStatus]
