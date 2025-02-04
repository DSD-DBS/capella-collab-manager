# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os

from capellacollab import openapi
from capellacollab.settings.modelsources.t4c.license_server import (
    exceptions as t4c_license_server_exceptions,
)
from capellacollab.users import exceptions as users_exceptions


def test_generate_exception_schema():
    os.environ["CAPELLACOLLAB_SKIP_OPENAPI_ERROR_RESPONSES"] = "0"

    schemas = openapi.get_exception_schemas()
    assert users_exceptions.UserNotFoundError.__name__ in schemas

    # Example for recursive exception subclass
    assert (
        t4c_license_server_exceptions.T4CLicenseServerWithNameAlreadyExistsError.__name__
        in schemas
    )
