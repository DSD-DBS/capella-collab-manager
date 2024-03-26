# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import logging

import fastapi
from fastapi import status
from fastapi.openapi import models as openapi_models
from fastapi.security import base as security_base
from fastapi.security import utils as security_utils
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import basic_auth, jwt_bearer
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

logger = logging.getLogger(__name__)


class OpenAPIFakeBase(security_base.SecurityBase):
    """Fake class to display the authentication methods in the OpenAPI docs

    fastAPI uses DependencyInjection together with the SecurityBase class
    to determine which authentication methods are available.
    More information in fastapi/dependencies/utils::get_sub_dependant
    """

    def __init__(self) -> None:
        pass

    def __call__(self) -> None:
        pass

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)


@dataclasses.dataclass()
class OpenAPIPersonalAccessToken(OpenAPIFakeBase):
    """Displays the personal access token as authentication method in the OpenAPI docs"""

    model = openapi_models.HTTPBase(
        scheme="basic",
        description="Can be used to authenticate with an personal access token",
    )
    scheme_name = "PersonalAccessToken"

    __hash__ = OpenAPIFakeBase.__hash__


@dataclasses.dataclass()
class OpenAPIBearerToken(OpenAPIFakeBase):
    """Displays the JWT Bearer token as authentication method in the OpenAPI docs"""

    model = openapi_models.HTTPBase(
        scheme="bearer",
    )
    scheme_name = "JWTBearer"

    __hash__ = OpenAPIFakeBase.__hash__


async def get_username(
    request: fastapi.Request,
    _unused1=fastapi.Depends(OpenAPIPersonalAccessToken()),
    _unused2=fastapi.Depends(OpenAPIBearerToken()),
) -> str:
    authorization = request.headers.get("Authorization")
    scheme, _ = security_utils.get_authorization_scheme_param(authorization)
    username = None
    match scheme.lower():
        case "basic":
            username = await basic_auth.HTTPBasicAuth()(request)
        case "bearer":
            username = await jwt_bearer.JWTBearer()(request)
        case _:
            raise fastapi.HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is none and username cannot be derived",
                headers={"WWW-Authenticate": "Bearer, Basic"},
            )

    assert username
    return username


class RoleVerification:
    def __init__(self, required_role: users_models.Role, verify: bool = True):
        self.required_role = required_role
        self.verify = verify

    def __call__(
        self,
        username: str = fastapi.Depends(get_username),
        db: orm.Session = fastapi.Depends(database.get_db),
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
        required_permission: (
            projects_users_models.ProjectUserPermission | None
        ) = None,
    ):
        self.required_role = required_role
        self.verify = verify
        self.required_permission = required_permission

    def __call__(
        self,
        project_slug: str,
        username: str = fastapi.Depends(get_username),
        db: orm.Session = fastapi.Depends(database.get_db),
    ) -> bool:
        if not (user := self._get_user_and_check(username, db)):
            return False

        if user.role == users_models.Role.ADMIN:
            return True

        if not (project := self._get_project_and_check(project_slug, db)):
            return False

        if self._is_internal_project_accessible(project):
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

        if not self._has_user_required_project_permissions(project_user):
            return False

        return True

    def _get_user_and_check(
        self, username: str, db: orm.Session
    ) -> users_models.DatabaseUser | None:
        user = users_crud.get_user_by_name(db, username)
        if not user and self.verify:
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"reason": f"User {username} was not found"},
            )
        return user

    def _get_project_and_check(
        self, project_slug: str, db: orm.Session
    ) -> projects_models.DatabaseProject | None:
        project = projects_crud.get_project_by_slug(db, project_slug)
        if not project and self.verify:
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"reason": f"The project {project_slug} was not found"},
            )
        return project

    def _is_internal_project_accessible(
        self, project: projects_models.DatabaseProject
    ) -> bool:
        return (
            project.visibility == projects_models.Visibility.INTERNAL
            and self.required_role
            == projects_users_models.ProjectUserRole.USER
            and self.required_permission
            in (None, projects_users_models.ProjectUserPermission.READ)
        )

    def _has_user_required_project_permissions(
        self, project_user: projects_users_models.ProjectUserAssociation
    ) -> bool:
        if not self.required_permission:
            return True

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
