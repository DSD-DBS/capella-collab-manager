# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import requests
from requests import auth as requests_auth

from capellacollab import config
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)

from . import exceptions, models


def get_t4c_status(
    instance: settings_t4c_models.DatabaseT4CInstance,
) -> models.GetSessionUsageResponse:
    try:
        r = requests.get(
            f"{instance.usage_api}/status/json",
            auth=requests_auth.HTTPBasicAuth(
                instance.username, instance.password
            ),
            timeout=config.config.requests.timeout,
        )
    except requests.Timeout:
        raise exceptions.LicenseServerTimeoutError()
    except requests.ConnectionError:
        raise exceptions.LicenseServerConnectionFailedError()

    # In older versions of the TeamForCapella license server,
    # the API endpoint returns 404 on success
    # -> We have to handle the error here manually
    if r.status_code != 404 and not r.ok:
        raise exceptions.LicenseServerInternalError()

    try:
        cur_status = r.json()["status"]

        if cur_status.get("message", "") == "No last status available.":
            raise exceptions.LicenseServerNoStatusError()

        if "used" in cur_status:
            return models.GetSessionUsageResponse(**cur_status)
    except KeyError:
        raise exceptions.LicenseServerNoStatusInResponse()
    except requests.JSONDecodeError:
        raise exceptions.LicenseServerResponseDecodeError()

    raise exceptions.LicenseServerUnknownError()
