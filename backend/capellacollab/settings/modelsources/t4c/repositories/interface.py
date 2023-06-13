# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.core.credentials import generate_password
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def list_repositories(instance: DatabaseT4CInstance):
    return make_request("GET", f"{instance.rest_api}/repositories", instance)[
        "repositories"
    ]


def create_repository(instance: DatabaseT4CInstance, name: str):
    return make_request(
        "POST",
        f"{instance.rest_api}/repositories",
        instance,
        json={
            "repositoryName": name,
            "authenticationType": "FILE",
            "authenticationData": {
                "users": [{"login": "admin", "password": generate_password()}]
            },
            "datasourceType": "H2_EMBEDDED",
        },
    )


def delete_repository(instance: DatabaseT4CInstance, name: str):
    return make_request(
        "DELETE",
        f"{instance.rest_api}/repositories/{urllib.parse.quote(name, safe='')}",
        instance,
    )


def start_repository(instance: DatabaseT4CInstance, name: str):
    return make_request(
        "GET",
        f"{instance.rest_api}/repositories/start/{urllib.parse.quote(name, safe='')}",
        instance,
    )


def stop_repository(instance: DatabaseT4CInstance, name: str):
    return make_request(
        "GET",
        f"{instance.rest_api}/repositories/stop/{urllib.parse.quote(name, safe='')}",
        instance,
    )


def add_user_to_repository(
    instance: DatabaseT4CInstance,
    repo_name: str,
    username: str,
    password: str = generate_password(),
    is_admin: bool = False,
):
    return make_request(
        "POST",
        f"{instance.rest_api}/users",
        instance,
        ignore_status_codes=[400],
        params={"repositoryName": repo_name},
        json={
            "id": username,
            "isAdmin": is_admin,
            "password": password,
        },
    )


def remove_user_from_repository(
    instance: DatabaseT4CInstance, repo_name: str, username: str
):
    make_request(
        "DELETE",
        f"{instance.rest_api}/users/{urllib.parse.quote(username, safe='')}",
        instance,
        ignore_status_codes=[404],
        params={"repositoryName": repo_name},
    )


def update_password_of_user(
    instance: DatabaseT4CInstance,
    repo_name: str,
    username: str,
    password: str,
):
    return make_request(
        "PUT",
        f"{instance.rest_api}/users/{urllib.parse.quote(username, safe='')}",
        instance,
        params={"repositoryName": repo_name},
        json={
            "id": username,
            "isAdmin": False,
            "password": password,
        },
    )


def make_request(
    method: str,
    url: str,
    instance: DatabaseT4CInstance,
    ignore_status_codes: list[int] | None = None,
    **kwargs,
):
    if not ignore_status_codes:
        ignore_status_codes = []

    r = requests.request(
        method,
        url,
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
        **kwargs,
    )

    if r.status_code not in ignore_status_codes:
        r.raise_for_status()

    return r.json()
