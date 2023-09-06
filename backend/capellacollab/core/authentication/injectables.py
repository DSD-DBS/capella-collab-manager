# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import fastapi
from fastapi import status

from capellacollab.core import database
from capellacollab.core.authentication import basic_auth, jwt_bearer
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

logger = logging.getLogger(__name__)


async def get_username(
    basic: tuple[str | None, fastapi.HTTPException | None] = fastapi.Depends(
        basic_auth.HTTPBasicAuth(auto_error=False)
    ),
    jwt: tuple[str | None, fastapi.HTTPException | None] = fastapi.Depends(
        jwt_bearer.JWTBearer(auto_error=False)
    ),
) -> str:
    jwt_username, jwt_error = jwt
    if jwt_username:
        return jwt_username

    basic_username, basic_error = basic
    if basic_username:
        return basic_username

    if jwt_error:
        raise jwt_error
    if basic_error:
        raise basic_error

    raise fastapi.HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is none and username cannot be derived",
        headers={"WWW-Authenticate": "Bearer, Basic"},
    )


async def get_username_not_injectable(request: fastapi.Request):
    basic = await basic_auth.HTTPBasicAuth(auto_error=False)(request)
    jwt = await jwt_bearer.JWTBearer(auto_error=False)(request)

    return await get_username(basic=basic, jwt=jwt)


class RoleVerification:
    def __init__(self, required_role: users_models.Role, verify: bool = True):
        self.required_role = required_role
        self.verify = verify

    def __call__(
        self,
        username=fastapi.Depends(get_username),
        db=fastapi.Depends(database.get_db),
    ) -> bool:
        if not (user := users_crud.get_user_by_name(db, username)):
            if self.verify:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"reason": f"User {username} was not found"},
                )
            return False

        if (
            user.role != users_models.Role.ADMIN
            and self.required_role == users_models.Role.ADMIN
        ):
            if self.verify:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "reason": "You need to be administrator for this transaction.",
                    },
                )
            return False
        return True


class ProjectRoleVerification:
    roles = [
        projects_users_models.ProjectUserRole.USER,
        projects_users_models.ProjectUserRole.MANAGER,
        projects_users_models.ProjectUserRole.ADMIN,
    ]

    def __init__(
        self,
        required_role: projects_users_models.ProjectUserRole,
        verify: bool = True,
        required_permission: projects_users_models.ProjectUserPermission
        | None = None,
    ):
        self.required_role = required_role
        self.verify = verify
        self.required_permission = required_permission

    def __call__(
        self,
        project_slug: str,
        username=fastapi.Depends(get_username),
        db=fastapi.Depends(database.get_db),
    ) -> bool:
        if not (user := users_crud.get_user_by_name(db, username)):
            if self.verify:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"reason": f"User {username} was not found"},
                )
            return False

        if user.role == users_models.Role.ADMIN:
            return True

        if not (
            project := projects_crud.get_project_by_slug(db, project_slug)
        ):
            if self.verify:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "reason": f"The project {project_slug} was not found"
                    },
                )
            return False

        if (
            project.visibility == projects_models.Visibility.INTERNAL
            and self.required_role
            == projects_users_models.ProjectUserRole.USER
            and self.required_permission
            in (None, projects_users_models.ProjectUserPermission.READ)
        ):
            return True

        project_user = projects_users_crud.get_project_user_association(
            db, project, user
        )
        if not project_user or self.roles.index(
            project_user.role
        ) < self.roles.index(self.required_role):
            if self.verify:
                raise fastapi.HTTPException(
                    status_code=403,
                    detail={
                        "reason": f"The role '{self.required_role.value}' in the project '{project_slug}' is required.",
                    },
                )
            return False

        if self.required_permission:
            if (
                project_user.permission
                == projects_users_models.ProjectUserPermission.READ
                and self.required_permission
                == projects_users_models.ProjectUserPermission.WRITE
            ):
                if self.verify:
                    raise fastapi.HTTPException(
                        status_code=403,
                        detail={
                            "reason": f"You need to have '{self.required_permission.value}'-access in the project!",
                        },
                    )
                return False

        return True
