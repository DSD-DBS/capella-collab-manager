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
            "authenticationType": "",
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
    r = get(
        f"{instance.rest_api}/repositories/stop/{name}",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()
