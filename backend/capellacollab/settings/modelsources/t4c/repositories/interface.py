# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import urllib.parse

import requests
from requests import auth

from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.settings.modelsources.t4c import models as t4c_models


def list_repositories(instance: t4c_models.DatabaseT4CInstance):
    return make_request("GET", f"{instance.rest_api}/repositories", instance)[
        "repositories"
    ]


def create_repository(instance: t4c_models.DatabaseT4CInstance, name: str):
    return make_request(
        "POST",
        f"{instance.rest_api}/repositories",
        instance,
        json={
            "repositoryName": name,
            "authenticationType": "FILE",
            "authenticationData": {
                "users": [
                    {
                        "login": "admin",
                        "password": credentials.generate_password(),
                    }
                ]
            },
            "datasourceType": "H2_EMBEDDED",
        },
    )


def delete_repository(instance: t4c_models.DatabaseT4CInstance, name: str):
    return make_request(
        "DELETE",
        f"{instance.rest_api}/repositories/{urllib.parse.quote(name, safe='')}",
        instance,
    )


def start_repository(instance: t4c_models.DatabaseT4CInstance, name: str):
    return make_request(
        "GET",
        f"{instance.rest_api}/repositories/start/{urllib.parse.quote(name, safe='')}",
        instance,
    )


def stop_repository(instance: t4c_models.DatabaseT4CInstance, name: str):
    return make_request(
        "GET",
        f"{instance.rest_api}/repositories/stop/{urllib.parse.quote(name, safe='')}",
        instance,
    )


def add_user_to_repository(
    instance: t4c_models.DatabaseT4CInstance,
    repo_name: str,
    username: str,
    password: str = credentials.generate_password(),
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
    instance: t4c_models.DatabaseT4CInstance, repo_name: str, username: str
):
    make_request(
        "DELETE",
        f"{instance.rest_api}/users/{urllib.parse.quote(username, safe='')}",
        instance,
        ignore_status_codes=[404],
        params={"repositoryName": repo_name},
    )


def update_password_of_user(
    instance: t4c_models.DatabaseT4CInstance,
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
    instance: t4c_models.DatabaseT4CInstance,
    ignore_status_codes: list[int] | None = None,
    **kwargs,
):
    if not ignore_status_codes:
        ignore_status_codes = []

    r = requests.request(
        method,
        url,
        auth=auth.HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
        **kwargs,
    )

    if r.status_code not in ignore_status_codes:
        r.raise_for_status()

    return r.json()
