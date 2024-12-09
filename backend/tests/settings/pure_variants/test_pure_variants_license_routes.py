# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import io

import pytest
from fastapi import testclient
from kubernetes import client as kubernetes_client
from sqlalchemy import orm

from capellacollab.settings.integrations.purevariants import (
    crud as pure_variants_crud,
)
from capellacollab.settings.integrations.purevariants import (
    models as pure_variants_models,
)


@pytest.mark.usefixtures("admin", "pure_variants_license")
def test_get_license(
    client: testclient.TestClient,
    pure_variants_license: pure_variants_models.DatabasePureVariantsLicenses,
):
    response = client.get(
        "/api/v1/settings/integrations/pure-variants",
    )

    assert response.is_success
    assert (
        response.json()["license_server_url"]
        == pure_variants_license.license_server_url
    )
    assert (
        response.json()["license_key_filename"]
        == pure_variants_license.license_key_filename
    )


@pytest.mark.usefixtures("admin")
def test_set_license_if_unset(client: testclient.TestClient):
    """Set the p::v license the first time"""

    response = client.patch(
        "/api/v1/settings/integrations/pure-variants",
        json={
            "license_server_url": "http://localhost:27000",
        },
    )

    assert response.is_success
    assert response.json()["license_server_url"] == "http://localhost:27000"


@pytest.mark.usefixtures("admin")
def test_set_license_if_set_already(
    db: orm.Session,
    client: testclient.TestClient,
    pure_variants_license: pure_variants_models.DatabasePureVariantsLicenses,
):
    """Update an existing license"""

    assert pure_variants_license.license_server_url != "http://localhost:27000"

    response = client.patch(
        "/api/v1/settings/integrations/pure-variants",
        json={
            "license_server_url": "http://localhost:27000",
        },
    )

    assert response.is_success
    assert response.json()["license_server_url"] == "http://localhost:27000"
    license_configuration = pure_variants_crud.get_pure_variants_configuration(
        db
    )
    assert license_configuration
    assert license_configuration.license_server_url == "http://localhost:27000"


class FakeKubernetesSecretClient:
    created_secrets_counter = 0
    deleted_secrets_counter = 0

    def create_namespaced_secret(
        self,
        namespace: str,  # pylint: disable=unused-argument
        secret: kubernetes_client.V1Secret,
    ):
        self.created_secrets_counter += 1
        return secret

    def delete_namespaced_secret(
        self,
        name: str,  # pylint: disable=unused-argument
        namespace: str,  # pylint: disable=unused-argument
    ):
        self.deleted_secrets_counter += 1
        return kubernetes_client.V1Status()


@pytest.fixture(name="mock_kubernetes_secret_client")
def fixture_mock_kubernetes_secret_client(monkeypatch: pytest.MonkeyPatch):
    client = FakeKubernetesSecretClient()
    monkeypatch.setattr(
        kubernetes_client.CoreV1Api,
        "create_namespaced_secret",
        client.create_namespaced_secret,
    )
    monkeypatch.setattr(
        kubernetes_client.CoreV1Api,
        "delete_namespaced_secret",
        client.delete_namespaced_secret,
    )
    return client


@pytest.mark.usefixtures("admin")
def test_upload_license_key(
    client: testclient.TestClient,
    mock_kubernetes_secret_client: FakeKubernetesSecretClient,
):
    """Upload a license key file"""

    file = io.BytesIO(b"some file content")
    file.name = "XYZ_license.lic"
    response = client.post(
        "/api/v1/settings/integrations/pure-variants/license-keys",
        files={"file": file},
    )

    assert response.is_success
    assert response.json()["license_key_filename"] == "XYZ_license.lic"
    assert mock_kubernetes_secret_client.deleted_secrets_counter == 1
    assert mock_kubernetes_secret_client.created_secrets_counter == 1


def delete_license_key(
    client: testclient.TestClient,
    mock_kubernetes_secret_client: FakeKubernetesSecretClient,
):
    """Delete the license key file"""

    response = client.delete(
        "/api/v1/settings/integrations/pure-variants/license-keys/0",
    )

    assert response.is_success
    assert mock_kubernetes_secret_client.deleted_secrets_counter == 1
