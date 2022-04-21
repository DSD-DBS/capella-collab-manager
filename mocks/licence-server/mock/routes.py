# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

router = APIRouter()


@router.get("/status/json", status_code=404)
def get_status():
    return {
        "version": "2.4.0-mock",
        "status": {
            "total": 30,
            "free": 26,
            "used": [
                {"user": "06-00-00-00-00-00", "lastSeen": "09/03/2022 17:00:00"},
                {"user": "07-00-00-00-00-00", "lastSeen": "09/03/2022 17:00:00"},
                {"user": "08-00-00-00-00-00", "lastSeen": "09/03/2022 17:00:00"},
                {"user": "09-00-00-00-00-00", "lastSeen": "09/03/2022 17:00:00"},
            ],
            "errors": [],
        },
    }


@router.get("/usage/json")
def get_usage():
    return {
        "version": "2.6.0.0000000000000",
        "status": [
            {
                "date": "2022-03-09",
                "hits": "1316",
                "maxAvailableTokens": "30",
                "minAvailableTokens": "16",
                "deny": "0",
            }
        ],
    }
