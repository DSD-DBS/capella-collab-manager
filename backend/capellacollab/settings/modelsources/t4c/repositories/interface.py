# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.core.credentials import generate_password
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def list_repositories(instance: DatabaseT4CInstance):
    r = requests.get(
        instance.rest_api + "/repositories",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()["repositories"]


def create_repository(instance: DatabaseT4CInstance, name: str):
    r = requests.post(
        instance.rest_api + "/repositories",
        json={
            "repositoryName": name,
            "authenticationType": "FILE",
            "authenticationData": {
                "users": [{"login": "admin", "password": generate_password()}]
            },
            "datasourceType": "H2_EMBEDDED",
        },
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()


def delete_repository(instance: DatabaseT4CInstance, name: str):
    r = requests.delete(
        f"{instance.rest_api}/repositories/{urllib.parse.quote(name, safe='')}",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()


def start_repository(instance: DatabaseT4CInstance, name: str):
    r = requests.get(
        f"{instance.rest_api}/repositories/start/{urllib.parse.quote(name, safe='')}",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()


def stop_repository(instance: DatabaseT4CInstance, name: str):
    r = requests.get(
        f"{instance.rest_api}/repositories/stop/{urllib.parse.quote(name, safe='')}",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()


def add_user_to_repository(
    instance: DatabaseT4CInstance,
    repository_name: str,
    username: str,
    password: str = generate_password(),
    is_admin: bool = False,
):
    r = requests.post(
        f"{instance.rest_api}/users",
        params={"repositoryName": repository_name},
        json={
            "id": username,
            "isAdmin": is_admin,
            "password": password,
        },
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )

    # No exception if user does already exist (status_code 400)
    if not r.ok and r.status_code != 400:
        raise requests.HTTPError(r)
    return r.json()


def remove_user_from_repository(
    instance: DatabaseT4CInstance, repository_name: str, username: str
):
    r = requests.delete(
        f"{instance.rest_api}/users/{urllib.parse.quote(username, safe='')}",
        params={"repositoryName": repository_name},
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    # No exception if user does not exist (status_code 404)
    if not r.ok and r.status_code != 404:
        raise requests.HTTPError(r)


def update_password_of_user(
    instance: DatabaseT4CInstance,
    repository_name: str,
    username: str,
    password: str,
):
    r = requests.put(
        f"{instance.rest_api}/users/{urllib.parse.quote(username, safe='')}",
        params={"repositoryName": repository_name},
        json={
            "id": username,
            "isAdmin": False,
            "password": password,
        },
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()
