# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.projects.permissions import (
    injectables as projects_injectables,
)

from . import models


def get_database_token_scopes(
    token: models.DatabaseUserToken,
) -> models.FineGrainedResource:
    model = models.FineGrainedResource.model_validate(token.scope)
    for project_scope in token.project_scopes:
        model.projects[project_scope.project.slug] = project_scope.scope
    return model


def get_actual_token_scopes(
    db: orm.Session,
    token: models.DatabaseUserToken,
) -> models.FineGrainedResource:
    global_scope = permissions_injectables.get_scope(token.user, token)
    model = models.FineGrainedResource.model_validate(global_scope)

    for project_scope in token.project_scopes:
        model.projects[project_scope.project.slug] = (
            projects_injectables.get_scope(
                token.user, token, global_scope, project_scope.project, db
            )
        )

    return model
