# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import requests
from fastapi import status
from requests import auth as requests_auth

from capellacollab import config
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)

from . import models


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
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "The connection to the license server timed out.",
                "technical": "The license server API timed out.",
                "err_code": "TIMEOUT",
            },
        )
    except requests.ConnectionError:
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "The connection to the license server failed.",
                "technical": "We failed to connect to the license server API.",
                "err_code": "CONNECTION_ERROR",
            },
        )

    # This API endpoint returns 404 on success -> We have to handle the error here manually
    if r.status_code != 404 and not r.ok:
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "Internal server error in the license server.",
                "technical": "The license server API returned an error.",
                "err_code": "T4C_ERROR",
            },
        )

    try:
        cur_status = r.json()["status"]

        if cur_status.get("message", "") == "No last status available.":
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "reason": "No status is available. This can happen during and after license server restarts.",
                    "technical": "The license server API returned no status.",
                    "err_code": "NO_STATUS",
                },
            )

        if "used" in cur_status:
            return models.GetSessionUsageResponse(**cur_status)
    except KeyError:
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "No status in response from license server.",
                "technical": "The license server response has no status.",
                "err_code": "NO_STATUS_JSON",
            },
        )
    except requests.JSONDecodeError:
        raise fastapi.HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "reason": "License server response could not be decoded.",
                "technical": "The returned status couldn’t be decoded.",
                "err_code": "DECODE_ERROR",
            },
        )

    raise fastapi.HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "reason": "An unknown error occurred when communicating with the license server.",
            "technical": "An unknown error has been encountered.",
            "err_code": "UNKNOWN_ERROR",
        },
    )
