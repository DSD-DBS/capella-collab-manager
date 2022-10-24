# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.users.crud as project_users
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects.crud import (
    get_project_by_name,
    get_project_by_slug,
)
from capellacollab.projects.users.models import (
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.sessions.database import get_session_by_id
from capellacollab.settings.modelsources.git import crud
from capellacollab.users.crud import get_user_by_name
from capellacollab.users.models import Role


class RoleVerification:
    def __init__(self, required_role: Role, verify: bool = True):
        self.required_role = required_role
        self.verify = verify

    def __call__(self, token=Depends(JWTBearer()), db=Depends(get_db)) -> bool:
        role = get_user_by_name(db=db, username=get_username(token)).role
        if role == Role.USER and self.required_role == Role.ADMIN:
            if self.verify:
                raise HTTPException(
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
        ProjectUserRole.USER,
        ProjectUserRole.MANAGER,
        ProjectUserRole.ADMIN,
    ]

    def __init__(
        self,
        required_role: ProjectUserRole,
        verify: bool = True,
        required_permission: t.Union[ProjectUserPermission, None] = None,
    ):
        self.required_role = required_role
        self.verify = verify
        self.required_permission = required_permission

    def __call__(
        self, project_slug: str, token=Depends(JWTBearer()), db=Depends(get_db)
    ) -> bool:
        user = get_user_by_name(db=db, username=get_username(token))

        if user.role == Role.ADMIN:
            return True

        project = get_project_by_slug(db, project_slug)
        project_user = project_users.get_user_of_project(db, project, user)

        # Check role
        if not project_user or self.roles.index(
            project_user.role
        ) < self.roles.index(self.required_role):
            if self.verify:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "reason": f"The role '{self.required_role.value}' in the project '{project_slug}' is required.",
                    },
                )
            return False

        # Check permission
        if self.required_permission:
            if (
                project_user.permission == ProjectUserPermission.READ
                and self.required_permission == ProjectUserPermission.WRITE
            ):
                if self.verify:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "reason": f"You need to have '{self.required_permission.value}'-access in the project!",
                        },
                    )
                return False

        return True


def verify_admin(token=Depends(JWTBearer()), db=Depends(get_db)):
    """
    .. deprecated:: 2.0.0
        Please use the `RoleVerification` class instead.
    """
    RoleVerification(required_role=Role.ADMIN)(token=token, db=db)


def verify_project_role(
    project: str,
    token: JWTBearer,
    db: Session,
    allowed_roles=None,
):
    """
    .. deprecated:: 2.0.0
        Please use the `ProjectRoleVerification` class instead.
    """
    if not allowed_roles:
        allowed_roles = ["user", "manager", "administrator"]
    required_role = ProjectUserRole.ADMIN
    if "manager" in allowed_roles:
        required_role = ProjectUserRole.MANAGER
    if "user" in allowed_roles:
        required_role = ProjectUserRole.USER

    project = get_project_by_name(db, project)
    return ProjectRoleVerification(required_role=required_role, verify=True)(
        project_slug=project.slug, token=token, db=db
    )


def verify_write_permission(
    project: str,
    token: JWTBearer,
    db: Session,
):
    """
    .. deprecated:: 2.0.0
        Please use the `ProjectRoleVerification` class instead.
    """
    project = get_project_by_name(db, project)
    return ProjectRoleVerification(
        required_role=ProjectUserRole.USER,
        verify=True,
        required_permission=ProjectUserPermission.WRITE,
    )(project_slug=project.slug, token=token, db=db)
