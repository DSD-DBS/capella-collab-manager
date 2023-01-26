# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import fastapi

from capellacollab.core import database
from capellacollab.core.authentication import jwt_bearer
from capellacollab.projects import crud as projects_crud
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

from . import helper


class RoleVerification:
    def __init__(self, required_role: users_models.Role, verify: bool = True):
        self.required_role = required_role
        self.verify = verify

    def __call__(
        self,
        token=fastapi.Depends(jwt_bearer.JWTBearer()),
        db=fastapi.Depends(database.get_db),
    ) -> bool:
        role = users_crud.get_user_by_name(
            db=db, username=helper.get_username(token)
        ).role
        if (
            role != users_models.Role.ADMIN
            and self.required_role == users_models.Role.ADMIN
        ):
            if self.verify:
                raise fastapi.HTTPException(
                    status_code=403,
                    detail={
                        "reason": "You need to be administrator for this transaction.",
                    },
                )
            else:
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
        token=fastapi.Depends(jwt_bearer.JWTBearer()),
        db=fastapi.Depends(database.get_db),
    ) -> bool:
        user = users_crud.get_user_by_name(db, helper.get_username(token))

        if user.role == users_models.Role.ADMIN:
            return True

        project = projects_crud.get_project_by_slug(db, project_slug)
        project_user = projects_users_crud.get_user_of_project(
            db, project, user
        )

        # Check role
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

        # Check permission
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
