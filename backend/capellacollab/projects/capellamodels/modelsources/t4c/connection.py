# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import json
import logging
import typing as t

import requests
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.core.credentials import generate_password

log = logging.getLogger(__name__)
cfg = config["modelsources"]["t4c"]

T4C_BACKEND_AUTHENTICATION = HTTPBasicAuth(cfg["username"], cfg["password"])


def add_user_to_repository(
    repository: str,
    username: str,
    password: str = generate_password(),
    is_admin: bool = False,
):
    r = requests.post(
        config["modelsources"]["t4c"]["restAPI"] + "/users",
        params={"repositoryName": repository},
        json={
            "id": username,
            "isAdmin": is_admin,
            "password": password,
        },
        auth=T4C_BACKEND_AUTHENTICATION,
        timeout=config["requests"]["timeout"],
    )

    # No exception if user does already exist (status_code 400)
    if not r.ok and r.status_code != 400:
        raise requests.HTTPError(r)
    return r.json()


def remove_user_from_repository(repository: str, username: str):
    r = requests.delete(
        config["modelsources"]["t4c"]["restAPI"] + "/users/" + username,
        params={"repositoryName": repository},
        auth=T4C_BACKEND_AUTHENTICATION,
        timeout=config["requests"]["timeout"],
    )
    # No exception if user does not exist (status_code 404)
    if not r.ok and r.status_code != 404:
        raise requests.HTTPError(r)


def update_password_of_user(repository: str, username: str, password: str):
    r = requests.put(
        config["modelsources"]["t4c"]["restAPI"] + "/users/" + username,
        params={"repositoryName": repository},
        json={
            "id": username,
            "isAdmin": False,
            "password": password,
        },
        auth=T4C_BACKEND_AUTHENTICATION,
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()
