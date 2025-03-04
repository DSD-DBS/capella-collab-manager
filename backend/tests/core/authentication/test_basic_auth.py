# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import datetime

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.permissions import models as permissions_models
from capellacollab.users import models as users_models
from capellacollab.users.tokens import crud as tokens_crud
from capellacollab.users.tokens import models as tokens_models


@pytest.fixture(name="pat_legacy")
def fixture_pat_legacy(
    db: orm.Session,
    user: users_models.DatabaseUser,
) -> tuple[tokens_models.DatabaseUserToken, str]:
    return tokens_crud.create_token(
        db,
        user,
        scope=permissions_models.GlobalScopes(),
        title="test",
        description="",
        expiration_date=None,
        source="test",
        legacy=True,
    )


@pytest.fixture(name="client_pat_legacy")
def fixture_client_pat_legacy(
    user: users_models.DatabaseUser,
    pat_legacy: tuple[tokens_models.DatabaseUserToken, str],
) -> testclient.TestClient:
    encoded_credentials = base64.b64encode(
        f"{user.name}:{pat_legacy[1]}".encode()
    ).decode()

    return testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )


def test_invalid_basic_auth_unknown_user(
    client_unauthenticated: testclient.TestClient,
) -> None:
    response = client_unauthenticated.get(
        "/api/v1/projects", auth=("unknown_user", "test")
    )

    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "BASIC_TOKEN_INVALID"


def test_use_pat(
    client_pat: testclient.TestClient,
):
    """Test to use a PAT as authentication against the API"""
    response = client_pat.get(
        "/api/v1/projects",
    )

    assert response.status_code == 200


def test_auth_with_invalid_pat(
    user: users_models.DatabaseUser,
    pat: tuple[tokens_models.DatabaseUserToken, str],
) -> None:
    """Try to authenticate with invalid PAT"""

    tmp_pat = pat[1].split("_")
    tmp_pat[1] = "invalid"
    modified_pat = "_".join(tmp_pat)

    encoded_credentials = base64.b64encode(
        f"{user.name}:{modified_pat}".encode()
    ).decode()

    client = testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )
    response = client.get(
        "/api/v1/projects",
    )
    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "BASIC_TOKEN_INVALID"


def test_auth_with_token_not_found(
    user: users_models.DatabaseUser,
) -> None:
    """Try to authenticate with non-existent PAT"""

    encoded_credentials = base64.b64encode(
        f"{user.name}:capellacollab_invalid_-1".encode()
    ).decode()

    client = testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )
    response = client.get(
        "/api/v1/projects",
    )
    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "BASIC_TOKEN_INVALID"


@pytest.mark.usefixtures("pat_legacy")
def test_auth_with_pat_legacy(
    db: orm.Session,
    user: users_models.DatabaseUser,
) -> None:
    """Try to use a legacy PAT (without token id)

    The legacy PAT iterates over the tokens;
    in this case we check that the second token is valid.
    """
    _, password = tokens_crud.create_token(
        db,
        user,
        scope=permissions_models.GlobalScopes(),
        title="test",
        description="",
        expiration_date=None,
        source="test",
        legacy=True,
    )

    encoded_credentials = base64.b64encode(
        f"{user.name}:{password}".encode()
    ).decode()

    client = testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )
    response = client.get(
        "/api/v1/projects",
    )
    assert response.status_code == 200


def test_auth_with_invalid_pat_legacy_token(
    user: users_models.DatabaseUser,
) -> None:
    """Try to authenticate with invalid PAT legacy token"""
    encoded_credentials = base64.b64encode(
        f"{user.name}:collabmanager_D5Sqm6rnE5S2fPMU58QmuLLLO1P7a5Wx".encode()
    ).decode()

    client = testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )
    response = client.get(
        "/api/v1/projects",
    )
    assert response.status_code == 401


def test_auth_with_invalid_structured_pat(
    user: users_models.DatabaseUser,
) -> None:
    encoded_credentials = base64.b64encode(
        f"{user.name}:some-randomly-structured-token".encode()
    ).decode()

    client = testclient.TestClient(
        app, headers={"Authorization": f"Basic {encoded_credentials}"}
    )
    response = client.get(
        "/api/v1/projects",
    )
    assert response.status_code == 401


def test_invalid_basic_auth_expired_token(
    client_pat: testclient.TestClient,
    pat: tuple[tokens_models.DatabaseUserToken, str],
) -> None:
    pat[0].expiration_date = datetime.datetime.now(
        tz=datetime.UTC
    ).date() - datetime.timedelta(days=1)
    response = client_pat.get("/api/v1/projects")

    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "PAT_EXPIRED"
