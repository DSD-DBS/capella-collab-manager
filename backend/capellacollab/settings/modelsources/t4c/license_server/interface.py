# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import requests

from capellacollab import config
from capellacollab.core import pydantic as core_pydantic

from . import exceptions


class T4CLicenseServerUsage(core_pydantic.BaseModel):
    free: int
    total: int


def get_t4c_license_server_version(usage_api: str) -> str | None:
    try:
        r = requests.get(
            f"{usage_api}/status/json",
            timeout=config.config.requests.timeout,
        )
    except requests.Timeout:
        return None
    except requests.ConnectionError:
        return None
    if r.status_code != 404 and not r.ok:
        return None

    data = r.json()
    license_server_version = data.get("version", None)
    return license_server_version


def get_t4c_license_server_usage(usage_api: str) -> T4CLicenseServerUsage:
    try:
        r = requests.get(
            f"{usage_api}/status/json",
            timeout=config.config.requests.timeout,
        )
    except requests.Timeout:
        raise exceptions.T4CLicenseServerTimeoutError()
    except requests.ConnectionError:
        raise exceptions.T4CLicenseServerConnectionFailedError()

    # In older versions of the TeamForCapella license server,
    # the API endpoint returns 404 on success
    # -> We have to handle the error here manually
    if r.status_code != 404 and not r.ok:
        raise exceptions.T4CLicenseServerInternalError()

    try:
        cur_status = r.json()["status"]

        if cur_status.get("message", "") == "No last status available.":
            raise exceptions.T4CLicenseServerNoStatusError()

        if "used" in cur_status:
            return T4CLicenseServerUsage(**cur_status)
    except KeyError:
        raise exceptions.T4CLicenseServerNoStatusInResponse()
    except requests.JSONDecodeError:
        raise exceptions.T4CLicenseServerResponseDecodeError()

    raise exceptions.T4CLicenseServerUnknownError()
