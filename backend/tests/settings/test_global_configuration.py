# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.settings.configuration import crud as configuration_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("admin")
def test_get_default_configuration(
    client: testclient.TestClient,
):
    """Test that the default configuration is returned if no configuration is set."""

    response = client.get("/api/v1/settings/configurations/global")

    assert response.status_code == 200
    assert response.json()["metadata"]["environment"] == "-"


@pytest.mark.usefixtures("admin")
def test_get_general_configuration(
    client: testclient.TestClient, db: orm.Session
):
    """Test that the configuration is returned from the database.
    If new attributes are added to the configuration,
    they should be returned with their default value as well.
    """

    configuration_crud.create_configuration(
        db, "global", {"metadata": {"environment": "test"}}
    )

    response = client.get("/api/v1/settings/configurations/global")

    assert response.status_code == 200
    assert response.json()["metadata"]["environment"] == "test"

    assert (
        response.json()["metadata"]["imprint_url"]
        == "https://example.com/imprint"  # Default value
    )


@pytest.mark.usefixtures("executor_name")
def test_get_configuration_schema(client: testclient.TestClient):
    response = client.get("/api/v1/settings/configurations/global/schema")

    assert response.status_code == 200
    assert "$defs" in response.json()


@pytest.mark.usefixtures("admin")
def test_update_general_configuration(
    client: testclient.TestClient,
):
    common_metadata = {
        "privacy_policy_url": "https://example.com/privacy-policy",
        "imprint_url": "https://example.com/imprint",
        "authentication_provider": "OAuth2",
        "environment": "-",
    }

    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "metadata": {
                "provider": "The best team in the world!",
                **common_metadata,
            }
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["metadata"]["provider"]
        == "The best team in the world!"
    )

    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "metadata": {
                "provider": "Still the best team in the world!",
                **common_metadata,
            }
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["metadata"]["provider"]
        == "Still the best team in the world!"
    )


@pytest.mark.usefixtures("admin")
def test_update_general_configuration_additional_properties_fails(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/settings/configurations/global", json={"test": "test"}
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"


@pytest.mark.usefixtures("admin")
def test_metadata_is_updated(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "metadata": {
                "privacy_policy_url": "https://example.com/privacy-policy",
                "imprint_url": "https://example.com/imprint",
                "provider": "The best team in the world!",
                "authentication_provider": "OAuth2",
                "environment": "test",
            }
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    assert response.json()["environment"] == "test"


@pytest.mark.usefixtures("admin")
def test_navbar_is_updated(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/settings/configurations/global",
        json={
            "navbar": {
                "external_links": [
                    {
                        "name": "Example",
                        "href": "https://example.com",
                        "role": "user",
                    }
                ]
            }
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/navbar")
    assert response.status_code == 200
    assert response.json()["external_links"][0] == {
        "name": "Example",
        "href": "https://example.com",
        "role": "user",
    }
