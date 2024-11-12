# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import testclient
from sqlalchemy import orm

from capellacollab.settings.configuration import crud as configuration_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


def test_set_own_beta_status_beta_disabled(
    client: testclient.TestClient,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    """
    Fail setting own beta status because beta is disabled
    """
    configuration_crud.create_configuration(
        db,
        "global",
        {"beta": {"enabled": False, "allow_self_enrollment": False}},
    )
    response = client.patch(
        f"/api/v1/users/{user.id}", json={"beta_tester": True}
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "BETA_TESTING_DISABLED"


def test_set_own_beta_status_no_self_enrollment(
    client: testclient.TestClient,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    """
    Fail setting own beta status because self serve beta is disabled
    """
    configuration_crud.create_configuration(
        db,
        "global",
        {"beta": {"enabled": True, "allow_self_enrollment": False}},
    )
    response = client.patch(
        f"/api/v1/users/{user.id}", json={"beta_tester": True}
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"]
        == "BETA_TESTING_SELF_ENROLLMENT_NOT_ALLOWED"
    )


def test_self_enroll_beta(
    client: testclient.TestClient,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    """
    Successfully set own beta status
    """
    configuration_crud.create_configuration(
        db,
        "global",
        {"beta": {"enabled": True, "allow_self_enrollment": True}},
    )
    response = client.patch(
        f"/api/v1/users/{user.id}", json={"beta_tester": True}
    )
    assert response.status_code == 200


def test_fail_enroll_other_people(
    client: testclient.TestClient,
    user: users_models.DatabaseUser,
    db: orm.Session,
):
    """
    Fail setting other people's beta status because not an admin
    """
    user2 = users_crud.create_user(db, "user2", "user2")

    configuration_crud.create_configuration(
        db,
        "global",
        {"beta": {"enabled": True, "allow_self_enrollment": True}},
    )
    response = client.patch(
        f"/api/v1/users/{user2.id}", json={"beta_tester": True}
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"]
        == "CHANGES_NOT_ALLOWED_FOR_OTHER_USERS"
    )


def test_admin_enroll_other_people(
    client: testclient.TestClient,
    admin: users_models.DatabaseUser,
    db: orm.Session,
):
    """
    Successfully set other people's beta status as an admin
    """
    user2 = users_crud.create_user(db, "user2", "user2")

    configuration_crud.create_configuration(
        db,
        "global",
        {"beta": {"enabled": True, "allow_self_enrollment": False}},
    )
    response = client.patch(
        f"/api/v1/users/{user2.id}", json={"beta_tester": True}
    )
    assert response.status_code == 200


def test_disable_beta_un_enroll(
    client: testclient.TestClient,
    admin: users_models.DatabaseUser,
    db: orm.Session,
):
    """
    When beta is disabled, all users should be unenrolled
    """
    configuration_crud.create_configuration(
        db,
        "global",
        {"beta": {"enabled": True, "allow_self_enrollment": False}},
    )
    response = client.patch(
        f"/api/v1/users/{admin.id}", json={"beta_tester": True}
    )
    assert response.status_code == 200

    client.put(
        "/api/v1/settings/configurations/global",
        json={"beta": {"enabled": False}},
    )

    response = client.get(f"/api/v1/users/{admin.id}")
    assert response.status_code == 200
    assert response.json()["beta_tester"] is False
