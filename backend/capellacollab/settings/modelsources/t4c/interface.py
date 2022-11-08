# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
from fastapi import HTTPException
from requests import ConnectionError, JSONDecodeError, Timeout, get
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.sessions.schema import GetSessionUsageResponse
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def get_t4c_status(instance: DatabaseT4CInstance) -> GetSessionUsageResponse:

    try:
        r = get(
            f"{instance.usage_api}/status/json",
            auth=HTTPBasicAuth(instance.username, instance.password),
            timeout=config["requests"]["timeout"],
        )
    except Timeout:
        raise HTTPException(
            502, {"reason": "The instance API timed out.", "code": "TIMEOUT"}
        )
    except ConnectionError:
        raise HTTPException(
            502,
            {
                "reason": "The instance API failed to connect.",
                "code": "CONNECTION_ERROR",
            },
        )

    # This API endpoint returns 404 on success -> We have to handle the error here manually
    if r.status_code != 404 and not r.ok:
        raise HTTPException(
            502,
            {"reason": "The instance returned an error.", "code": "T4C_ERROR"},
        )

    try:
        status = r.json()["status"]

        if status.get("message", "") == "No last status available.":
            raise HTTPException(
                502,
                {
                    "reason": "The instance returned no status.",
                    "code": "NO_STATUS",
                },
            )

        if "used" in status:
            return GetSessionUsageResponse(**status)
    except KeyError:
        raise HTTPException(
            502,
            {
                "reason": "The instance has no status.",
                "code": "NO_STATUS_JSON",
            },
        )
    except JSONDecodeError:
        raise HTTPException(
            502,
            {
                "reason": "The returned status couldn’t be decoded.",
                "code": "DECODE_ERROR",
            },
        )

    raise HTTPException(
        500,
        {
            "reason": "An unknown error has been encountered.",
            "code": "UNKNOWN_ERROR",
        },
    )
