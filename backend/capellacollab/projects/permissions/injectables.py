# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

from . import crud, exceptions, models, permissions


def get_scope(
    authentication_information: tuple[
        users_models.DatabaseUser, tokens_models.DatabaseUserToken | None
    ] = fastapi.Depends(
        auth_injectables.AuthenticationInformationValidation()
    ),
    global_scope: permissions_models.GlobalScopes = fastapi.Depends(
        permissions_injectables.get_scope
    ),
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.ProjectUserScopes:
    user, token = authentication_information

    inherited_global_scope = permissions.inherit_global_permissions(
        global_scope
    )

    project_user = projects_users_crud.get_project_user_association(
        db, project, user
    )
    derived_project_scope = permissions.derive_project_permissions_from_role(
        project, project_user
    )

    if token:
        project_token = crud.get_project_token(db, project, token)
        if not project_token:
            return models.ProjectUserScopes()

        return inherited_global_scope | (
            project_token.scope & derived_project_scope
        )

    return inherited_global_scope | derived_project_scope


@dataclasses.dataclass(eq=False)
class ProjectPermissionValidation:
    required_scope: models.ProjectUserScopes

    def __call__(
        self,
        project_scope: models.ProjectUserScopes = fastapi.Depends(get_scope),
        project: projects_models.DatabaseProject = fastapi.Depends(
            projects_injectables.get_existing_project
        ),
    ) -> None:
        actual_scope = project_scope.model_dump()

        for scope, perms in self.required_scope:
            for perm, verbs in perms:
                for verb in verbs:
                    if verb not in actual_scope[scope][perm]:
                        raise exceptions.InsufficientProjectPermissionError(
                            perm,
                            verbs,
                            project_name=project.name,
                        )

    def __repr__(self) -> str:
        required_permissions = []
        for perms, verbs in self.required_scope:
            for verb in verbs:
                required_permissions.append(f"`{perms}:{verb.lower()}`")
        return ", ".join(required_permissions)