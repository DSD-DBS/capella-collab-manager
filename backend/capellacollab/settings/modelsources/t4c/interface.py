# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
import requests
from fastapi import HTTPException
from requests import ConnectionError, JSONDecodeError, Timeout
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.sessions.schema import GetSessionUsageResponse
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def get_t4c_status(instance: DatabaseT4CInstance) -> GetSessionUsageResponse:

    try:
        r = requests.get(
            f"{instance.usage_api}/status/json",
            auth=HTTPBasicAuth(instance.username, instance.password),
            timeout=config["requests"]["timeout"],
        )
    except Timeout:
        raise HTTPException(
            502,
            {
                "reason": "The connection to the license server timed out.",
                "technical": "The license server API timed out.",
                "err_code": "TIMEOUT",
            },
        )
    except ConnectionError:
        raise HTTPException(
            502,
            {
                "reason": "The connection to the license server failed.",
                "technical": "We failed to connect to the license server API.",
                "err_code": "CONNECTION_ERROR",
            },
        )

    # This API endpoint returns 404 on success -> We have to handle the error here manually
    if r.status_code != 404 and not r.ok:
        raise HTTPException(
            502,
            {
                "reason": "Internal server error in the license server.",
                "technical": "The license server API returned an error.",
                "err_code": "T4C_ERROR",
            },
        )

    try:
        status = r.json()["status"]

        if status.get("message", "") == "No last status available.":
            raise HTTPException(
                502,
                {
                    "reason": "No status is available. This can happen during and after license server restarts.",
                    "technical": "The license server API returned no status.",
                    "err_code": "NO_STATUS",
                },
            )

        if "used" in status:
            return GetSessionUsageResponse(**status)
    except KeyError:
        raise HTTPException(
            502,
            {
                "reason": "No status in response from license server.",
                "technical": "The license server response has no status.",
                "err_code": "NO_STATUS_JSON",
            },
        )
    except JSONDecodeError:
        raise HTTPException(
            502,
            {
                "reason": "License server response could not be decoded.",
                "technical": "The returned status couldn’t be decoded.",
                "err_code": "DECODE_ERROR",
            },
        )

    raise HTTPException(
        502,
        {
            "reason": "An unknown error occurred when communicating with the license server.",
            "technical": "An unknown error has been encountered.",
            "err_code": "UNKNOWN_ERROR",
        },
    )
