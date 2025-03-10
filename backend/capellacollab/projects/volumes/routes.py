# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
import uuid

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)

from . import crud, exceptions, injectables, models, workspace

router = fastapi.APIRouter()


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    shared_volumes={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
    response_model=models.ProjectVolume | None,
)
def get_project_volume(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
) -> models.DatabaseProjectVolume | None:
    return crud.get_project_volume(db, project)


@router.get(
    "/{project_volume_id}",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    shared_volumes={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
    response_model=models.ProjectVolume,
)
def get_existing_project_volume(
    project_volume: t.Annotated[
        models.DatabaseProjectVolume,
        fastapi.Depends(injectables.get_existing_project_volume),
    ],
) -> models.DatabaseProjectVolume:
    return project_volume


@router.post(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    shared_volumes={permissions_models.UserTokenVerb.CREATE}
                )
            )
        )
    ],
    response_model=models.ProjectVolume,
)
def create_project_volume(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
):
    if crud.get_project_volume(db, project):
        raise exceptions.OnlyOneVolumePerProjectError(project.slug)
    size = "2Gi"
    pvc_name = workspace.create_shared_workspace(
        str(uuid.uuid4()), project, size
    )
    return crud.create_project_volume(db, project, pvc_name, size)


@router.delete(
    "/{project_volume_id}",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    shared_volumes={permissions_models.UserTokenVerb.DELETE}
                )
            )
        )
    ],
    status_code=204,
)
def delete_project_volume(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project_volume: t.Annotated[
        models.DatabaseProjectVolume,
        fastapi.Depends(injectables.get_existing_project_volume),
    ],
):
    workspace.delete_shared_workspace(project_volume.pvc_name)
    return crud.delete_project_volume(db, project_volume)
