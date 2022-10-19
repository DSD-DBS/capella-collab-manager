# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy.orm import Session

import capellacollab.extensions.modelsources.git.crud as git_model_crud
import capellacollab.extensions.modelsources.t4c.connection as t4c_ext
import capellacollab.projects.models as project_models
import capellacollab.projects.users.models as users_schema
from capellacollab.projects.users.models import ProjectUserPermission


def get_permission(
    repo_permission: ProjectUserPermission,
    project: str,
    db: Session,
) -> t.List[ProjectUserPermission]:
    allowed_permissions: t.List[ProjectUserPermission] = []

    if git_model_crud.get_primary_gitmodel_of_capellamodels(db, project):
        allowed_permissions.append(ProjectUserPermission.READ)

    if repo_permission == ProjectUserPermission.WRITE:
        allowed_permissions.append(ProjectUserPermission.WRITE)
    return allowed_permissions
