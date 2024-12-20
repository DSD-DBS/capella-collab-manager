# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.users import models as projects_users_models
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER
            )
        )
    ]
)


@router.get(
    "",
)
def get_project_tools(
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
) -> list[models.ProjectTool]:
    tools = [models.ProjectTool.model_validate(tool) for tool in project.tools]

    for model in project.models:
        if not model.version:
            continue

        tool = next(
            (
                tool
                for tool in tools
                if model.version.id == tool.tool_version.id
            ),
            None,
        )

        if not tool:
            tool = models.ProjectTool(
                id=None,
                tool_version=tools_models.SimpleToolVersion.model_validate(
                    model.version
                ),
                tool=tools_models.Tool.model_validate(model.version.tool),
                used_by=[],
            )
            tools.append(tool)

        tool.used_by.append(
            toolmodels_models.SimpleToolModelWithoutProject.model_validate(
                model
            )
        )

    return tools


@router.post(
    "",
    response_model=models.ProjectTool,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def link_tool_to_project(
    body: models.PostProjectToolRequest,
    db: orm.Session = fastapi.Depends(database.get_db),
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
) -> models.DatabaseProjectToolAssociation:
    tool_version = tools_injectables.get_existing_tool_version(
        body.tool_id, body.tool_version_id, db
    )
    if crud.get_project_tool_by_project_and_tool_version(
        db, project, tool_version
    ):
        raise exceptions.ToolAlreadyLinkedToProjectError()
    return crud.create_project_tool(db, project, tool_version)


@router.delete(
    "/{project_tool_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ],
)
def delete_tool_from_project(
    db: orm.Session = fastapi.Depends(database.get_db),
    project_tool: models.DatabaseProjectToolAssociation = fastapi.Depends(
        injectables.get_existing_project_tool
    ),
) -> None:
    crud.delete_project_tool(db, project_tool)
