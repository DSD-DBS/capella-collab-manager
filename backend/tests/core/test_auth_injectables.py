# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pytest
from sqlalchemy import orm

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="verify", params=[True, False])
def fixture_verify(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(name="admin2")
def fixture_admin2(db: orm.Session) -> users_models.DatabaseUser:
    return users_crud.create_user(
        db, "admin2", "admin2", None, users_models.Role.ADMIN
    )


def test_role_verification_user_not_found(db: orm.Session, verify: bool):
    verification = auth_injectables.RoleVerification(
        required_role=users_models.Role.USER, verify=verify
    )

    if verify:
        with pytest.raises(fastapi.HTTPException):
            verification("nonexistent_user", db)
    else:
        assert verification("nonexistent_user", db) is False


def test_role_verification_required_admin(
    db: orm.Session,
    verify: bool,
    user2: users_models.DatabaseUser,
    admin2: users_models.DatabaseUser,
):
    verification = auth_injectables.RoleVerification(
        required_role=users_models.Role.ADMIN, verify=verify
    )

    if verify:
        with pytest.raises(fastapi.HTTPException):
            verification(user2.name, db)
    else:
        assert verification(user2.name, db) is False

    assert verification(admin2.name, db) is True


def test_role_verification_required_user(
    db: orm.Session,
    verify: bool,
    user2: users_models.DatabaseUser,
    admin2: users_models.DatabaseUser,
):
    verification = auth_injectables.RoleVerification(
        required_role=users_models.Role.USER, verify=verify
    )

    assert verification(user2.name, db) is True
    assert verification(admin2.name, db) is True


def test_project_role_verification_user_not_found(
    db: orm.Session, verify: bool, project: projects_models.DatabaseProject
):
    verification = auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.USER, verify=verify
    )

    if verify:
        with pytest.raises(fastapi.HTTPException):
            verification(project.name, "nonexistent_user", db)
    else:
        assert verification(project.name, "nonexistent_user", db) is False


def test_project_role_verification_project_not_found(
    db: orm.Session, verify: bool, user: users_models.DatabaseUser
):
    verification = auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.USER, verify=verify
    )

    if verify:
        with pytest.raises(fastapi.HTTPException):
            verification("nonexistent_project", user.name, db)
    else:
        assert verification("nonexistent_project", user.name, db) is False


@pytest.fixture(name="project_user_lead")
def fixture_project_user_lead(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_users_models.ProjectUserAssociation:
    user = users_crud.create_user(
        db,
        "project_user_lead",
        "project_user_lead",
        None,
        users_models.Role.USER,
    )
    return projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )


@pytest.fixture(name="project_user_write")
def fixture_project_user_write(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_users_models.ProjectUserAssociation:
    user = users_crud.create_user(
        db,
        "project_user_write",
        "project_user_write",
        None,
        users_models.Role.USER,
    )
    return projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )


@pytest.fixture(name="project_user_read")
def fixture_project_user_read(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_users_models.ProjectUserAssociation:
    user = users_crud.create_user(
        db,
        "project_user_read",
        "project_user_read",
        None,
        users_models.Role.USER,
    )
    return projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.READ,
    )


def test_project_role_verification_required_lead_write(
    db: orm.Session,
    verify: bool,
    user2: users_models.DatabaseUser,
    admin2: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    project_user_lead: projects_users_models.ProjectUserAssociation,
    project_user_write: projects_users_models.ProjectUserAssociation,
    project_user_read: projects_users_models.ProjectUserAssociation,
):
    verification = auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.MANAGER,
        verify=verify,
    )

    assert verification(project.slug, admin2.name, db) is True
    assert verification(project.slug, project_user_lead.user.name, db) is True

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        project_user_write.user.name,
        db,
    )

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        project_user_read.user.name,
        db,
    )

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        user2.name,
        db,
    )


def test_project_role_verification_required_user_write(
    db: orm.Session,
    verify: bool,
    user2: users_models.DatabaseUser,
    admin2: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    project_user_lead: projects_users_models.ProjectUserAssociation,
    project_user_write: projects_users_models.ProjectUserAssociation,
    project_user_read: projects_users_models.ProjectUserAssociation,
):
    verification = auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.USER,
        verify=verify,
        required_permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    assert verification(project.slug, admin2.name, db) is True
    assert verification(project.slug, project_user_lead.user.name, db) is True
    assert verification(project.slug, project_user_write.user.name, db) is True

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        project_user_read.user.name,
        db,
    )

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        user2.name,
        db,
    )


def test_project_role_verification_required_user_read(
    db: orm.Session,
    verify: bool,
    user2: users_models.DatabaseUser,
    admin2: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    project_user_lead: projects_users_models.ProjectUserAssociation,
    project_user_write: projects_users_models.ProjectUserAssociation,
    project_user_read: projects_users_models.ProjectUserAssociation,
):
    verification = auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.USER,
        verify=verify,
        required_permission=projects_users_models.ProjectUserPermission.READ,
    )

    assert verification(project.slug, admin2.name, db) is True
    assert verification(project.slug, project_user_lead.user.name, db) is True
    assert verification(project.slug, project_user_write.user.name, db) is True
    assert verification(project.slug, project_user_read.user.name, db) is True

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        user2.name,
        db,
    )


def test_project_role_verification_required_user_no_permission(
    db: orm.Session,
    verify: bool,
    user2: users_models.DatabaseUser,
    admin2: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    project_user_lead: projects_users_models.ProjectUserAssociation,
    project_user_write: projects_users_models.ProjectUserAssociation,
    project_user_read: projects_users_models.ProjectUserAssociation,
):
    verification = auth_injectables.ProjectRoleVerification(
        required_role=projects_users_models.ProjectUserRole.USER,
        verify=verify,
    )

    assert verification(project.slug, admin2.name, db) is True
    assert verification(project.slug, project_user_lead.user.name, db) is True
    assert verification(project.slug, project_user_write.user.name, db) is True
    assert verification(project.slug, project_user_read.user.name, db) is True

    assert_project_verification_fails(
        verify,
        verification,
        project.slug,
        user2.name,
        db,
    )


def assert_project_verification_fails(
    verify: bool,
    verification: auth_injectables.ProjectRoleVerification,
    project_slug: str,
    username: str,
    db: orm.Session,
):
    if verify:
        with pytest.raises(fastapi.HTTPException):
            verification(project_slug, username, db)
    else:
        assert verification(project_slug, username, db) is False
