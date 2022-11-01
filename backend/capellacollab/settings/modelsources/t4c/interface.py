# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from requests import JSONDecodeError, Timeout, get
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def get_t4c_status(instance: DatabaseT4CInstance):

    try:
        r = get(
            f"{instance.usage_api}/status/json",
            auth=HTTPBasicAuth(instance.username, instance.password),
            timeout=config["requests"]["timeout"],
        )
    except Timeout:
        return {"free": -1, "total": -1, "used": [], "errors": ["TIMEOUT"]}
    except ConnectionError:
        return {
            "free": -1,
            "total": -1,
            "used": [],
            "errors": ["CONNECTION_ERROR"],
        }

    # This API endpoints returns 404 on success -> We have to handle the errors here manually
    if r.status_code != 404 and not r.ok:
        return {"free": -1, "total": -1, "used": [], "errors": ["T4C_ERROR"]}

    try:
        status = r.json()["status"]

        if status.get("message", "") == "No last status available.":
            return {
                "free": -1,
                "total": -1,
                "used": [],
                "errors": ["NO_STATUS"],
            }

        if "used" in status:
            return status
    except KeyError:
        return {
            "free": -1,
            "total": -1,
            "used": [],
            "errors": ["NO_STATUS_JSON"],
        }
    except JSONDecodeError:
        return {
            "free": -1,
            "total": -1,
            "used": [],
            "errors": ["DECODE_ERROR"],
        }

    return {"free": -1, "total": -1, "used": [], "errors": ["UNKNOWN_ERROR"]}
