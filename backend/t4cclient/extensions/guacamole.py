# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import requests
from requests.auth import HTTPBasicAuth
from t4cclient.config import config
from t4cclient.core.credentials import generate_password

cfg = config["extensions"]["guacamole"]
GUACAMOLE_PREFIX = cfg["baseURI"] + "/api/session/data/postgresql"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
proxies = {
    "http": None,
    "https": None,
}


def get_admin_token() -> str:
    r = requests.post(
        cfg["baseURI"] + "/api/tokens",
        auth=HTTPBasicAuth(cfg["username"], cfg["password"]),
        headers=headers,
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )
    r.raise_for_status()
    return r.json()["authToken"]


def get_token(username: str, password: str) -> str:
    r = requests.post(
        cfg["baseURI"] + "/api/tokens",
        auth=HTTPBasicAuth(username, password),
        headers=headers,
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )
    r.raise_for_status()
    return r.json()


def create_user(
    token: str,
    username: str = generate_password(10),
    password: str = generate_password(128),
) -> None:
    r = requests.post(
        GUACAMOLE_PREFIX + "/users?token=" + token,
        json={"username": username, "password": password, "attributes": {}},
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )
    r.raise_for_status()
    return r.json()


def assign_user_to_connection(token: str, username: str, connection_id: str):
    r = requests.patch(
        f"{GUACAMOLE_PREFIX}/users/{username}/permissions?token={token}",
        json=[
            {
                "op": "add",
                "path": f"/connectionPermissions/{connection_id}",
                "value": "READ",
            }
        ],
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )
    r.raise_for_status()


def delete_user(token: str, username: str):
    r = requests.delete(
        f"{GUACAMOLE_PREFIX}/users/{username}?token={token}",
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )
    r.raise_for_status()
    return r.json()


def delete_connection(token: str, connection_name: str):
    r = requests.delete(
        f"{GUACAMOLE_PREFIX}/connections/{connection_name}?token={token}",
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )
    r.raise_for_status()
    return r.json()


def create_connection(
    token: str,
    rdp_password: str,
    rdp_host: str,
    rdp_port: int,
):
    r = requests.post(
        f"{GUACAMOLE_PREFIX}/connections?token={token}",
        json={
            "parentIdentifier": "ROOT",
            "name": str(uuid.uuid4()),
            "protocol": "rdp",
            "parameters": {
                "hostname": rdp_host,
                "username": "techuser",
                "password": rdp_password,
                "port": rdp_port,
                "ignore-cert": True,
                "server-layout": "de-de-qwertz",
            },
            "attributes": {},
        },
        timeout=config["requests"]["timeout"],
        proxies=proxies,
    )

    r.raise_for_status()
    return r.json()
