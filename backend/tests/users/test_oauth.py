# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import testclient
from sqlalchemy import orm

from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


def test_validate_tokens_routes(
    db: orm.Session,
    client: testclient.TestClient,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    response = client.get("/api/v1/authentication/tokens")

    assert response.status_code == 200
    assert response.json() == executor_name
