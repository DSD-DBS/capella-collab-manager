# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects.permissions import crud as project_permissions_crud
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

from . import crud, injectables, models, util

router = fastapi.APIRouter()


@router.post(
    "",
    response_model=models.UserTokenWithPassword,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        tokens={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
        )
    ],
)
def create_token_for_user(
    post_token: models.PostToken,
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.UserTokenWithPassword:
    projects = [
        (
            projects_injectables.get_existing_project(project_slug, db),
            project_scope,
        )
        for project_slug, project_scope in post_token.scopes.projects.items()
    ]

    token, password = crud.create_token(
        db,
        user,
        scope=permissions_models.GlobalScopes.model_validate(
            post_token.scopes
        ),
        description=post_token.description,
        expiration_date=post_token.expiration_date,
        source=post_token.source,
    )

    for project, project_scope in projects:
        project_permissions_crud.create_personal_access_token_link(
            db, project, token, project_scope
        )

    return models.UserTokenWithPassword(
        id=token.id,
        user_id=token.user_id,
        created_at=token.created_at,
        expiration_date=token.expiration_date,
        requested_scopes=util.get_database_token_scopes(token),
        actual_scopes=util.get_actual_token_scopes(db, token),
        description=token.description,
        source=token.source,
        password=password,
    )


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        tokens={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_all_tokens_of_user(
    token_list: abc.Sequence[models.DatabaseUserToken] = fastapi.Depends(
        injectables.get_own_user_tokens
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.UserToken]:
    return [
        models.UserToken(
            id=token.id,
            user_id=token.user_id,
            created_at=token.created_at,
            expiration_date=token.expiration_date,
            requested_scopes=util.get_database_token_scopes(token),
            actual_scopes=util.get_actual_token_scopes(db, token),
            description=token.description,
            source=token.source,
        )
        for token in token_list
    ]


@router.delete(
    "/{token_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    user=permissions_models.UserScopes(
                        tokens={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_token_for_user(
    token: models.DatabaseUserToken = fastapi.Depends(
        injectables.get_exisiting_own_user_token
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> None:
    return crud.delete_token(db, token)
