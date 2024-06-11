# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status


@pytest.fixture(name="mock_license_server")
def fixture_mock_license_server():
    with responses.RequestsMock() as rsps:
        rsps.get(
            "http://localhost:8086/status/json",
            status=status.HTTP_200_OK,
            json={"status": {"used": 1, "free": 19, "total": 20}},
        )
        yield rsps
