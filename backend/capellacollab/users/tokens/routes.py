# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
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

from . import crud, exceptions, injectables, models, util

user_token_router = fastapi.APIRouter()
global_token_router = fastapi.APIRouter()


@user_token_router.post(
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
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(user_injectables.get_own_user),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
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
        title=post_token.title,
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
        user=users_models.User.model_validate(token.user),
        title=token.title,
        created_at=token.created_at,
        expiration_date=token.expiration_date,
        requested_scopes=util.get_database_token_scopes(token),
        actual_scopes=util.get_actual_token_scopes(db, token),
        description=token.description,
        source=token.source,
        password=password,
        managed=token.managed,
    )


@user_token_router.get(
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
    token_list: t.Annotated[
        abc.Sequence[models.DatabaseUserToken],
        fastapi.Depends(injectables.get_own_user_tokens),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.UserToken]:
    return [
        models.UserToken(
            id=token.id,
            user=users_models.User.model_validate(token.user),
            title=token.title,
            created_at=token.created_at,
            expiration_date=token.expiration_date,
            requested_scopes=util.get_database_token_scopes(token),
            actual_scopes=util.get_actual_token_scopes(db, token),
            description=token.description,
            source=token.source,
            managed=token.managed,
        )
        for token in token_list
    ]


@user_token_router.delete(
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
    token: t.Annotated[
        models.DatabaseUserToken,
        fastapi.Depends(injectables.get_existing_own_user_token),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
) -> None:
    if (
        token.managed
        and permissions_models.UserTokenVerb.DELETE
        not in global_scope.admin.personal_access_tokens
    ):
        raise exceptions.ManagedTokensRestrictionError(token.id)
    return crud.delete_token(db, token)


@global_token_router.get(
    "",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        personal_access_tokens={
                            permissions_models.UserTokenVerb.GET
                        }
                    )
                )
            ),
        )
    ],
)
def get_all_tokens(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.UserToken]:
    return [
        models.UserToken(
            id=token.id,
            user=users_models.User.model_validate(token.user),
            title=token.title,
            created_at=token.created_at,
            expiration_date=token.expiration_date,
            requested_scopes=util.get_database_token_scopes(token),
            actual_scopes=util.get_actual_token_scopes(db, token),
            description=token.description,
            source=token.source,
            managed=token.managed,
        )
        for token in crud.get_all_tokens(db)
    ]


@global_token_router.delete(
    "/{token_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        personal_access_tokens={
                            permissions_models.UserTokenVerb.DELETE
                        }
                    )
                )
            ),
        )
    ],
)
def delete_token_globally(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    token: t.Annotated[
        models.DatabaseUserToken,
        fastapi.Depends(injectables.get_existing_global_token),
    ],
) -> None:
    crud.delete_token(db, token)
