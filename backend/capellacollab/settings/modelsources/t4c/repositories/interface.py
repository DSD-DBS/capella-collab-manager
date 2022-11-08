# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from requests import delete, get, post
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def list_repositories(instance: DatabaseT4CInstance):
    r = get(
        instance.rest_api + "/repositories",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()["repositories"]


def create_repository(instance: DatabaseT4CInstance, name: str):
    r = post(
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
    r = delete(
        f"{instance.rest_api}/repositories/{name}",
        auth=HTTPBasicAuth(instance.username, instance.password),
        timeout=config["requests"]["timeout"],
    )
    r.raise_for_status()
    return r.json()


def start_repository(instance: DatabaseT4CInstance, name: str):
    r = get(
        f"{instance.rest_api}/repositories/start/{name}",
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
