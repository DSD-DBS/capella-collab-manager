import json
import logging
import typing as t

import requests
from requests.auth import HTTPBasicAuth
from t4cclient import config
from t4cclient.core.credential_manager import generate_password

log = logging.getLogger(__name__)

T4C_BACKEND_AUTHENTICATION = HTTPBasicAuth(
    config.T4C_SERVER_USERNAME, config.T4C_SERVER_PASSWORD
)


def get_t4c_status():
    try:
        r = requests.get(
            config.T4C_USAGE_API + "/status/json", auth=T4C_BACKEND_AUTHENTICATION
        )
    except requests.exceptions.Timeout:
        return {"free": -1, "total": -1, "used": [], "errors": ["TIMEOUT"]}
    except requests.exceptions.ConnectionError:
        return {"free": -1, "total": -1, "used": [], "errors": ["CONNECTION_ERROR"]}

    # This API endpoints returns 404 on success -> We have to handle the errors here manually
    if r.status_code != 404 and not r.ok:
        log.error(
            "Licence server returned status code %s: %s",
            r.status_code,
            r.content.decode("ascii"),
        )
        return {"free": -1, "total": -1, "used": [], "errors": ["T4C_ERROR"]}

    try:
        status = r.json()["status"]

        if status.get("message", "") == "No last status available.":
            return {"free": -1, "total": -1, "used": [], "errors": ["NO_STATUS"]}

        if "used" in status:
            return status
    except KeyError:
        log.exception("No status available")
        log.info("Response from T4C is %s", r.content.decode("ascii"))
        return {"free": -1, "total": -1, "used": [], "errors": ["NO_STATUS_JSON"]}
    except json.JSONDecodeError:
        log.exception("Cannot decode T4C status")
        log.info("Response from T4C is %s", r.content.decode("ascii"))
        return {"free": -1, "total": -1, "used": [], "errors": ["DECODE_ERROR"]}

    return {"free": -1, "total": -1, "used": [], "errors": ["UNKNOWN_ERROR"]}


def fetch_last_seen(mac_addr: str):
    try:
        status = get_t4c_status()
        if "errors" in status:
            return str(status["errors"][0])
        list_with_mac = [
            user["lastSeen"]
            for user in get_t4c_status()["used"]
            if user["user"] == mac_addr.upper().replace(":", "-")
        ]
        if list_with_mac:
            return list_with_mac[0]
        return "No T4C Session found"
    except Exception:
        log.exception("Unexpected exception")
        return "UNKNOWN_ERROR"


def add_user_to_repository(
    repository: str, username: str, password: str = generate_password()
):
    r = requests.post(
        config.T4C_REST_API + "/users",
        params={"repositoryName": repository},
        json={
            "id": username,
            "isAdmin": False,
            "password": password,
        },
        auth=T4C_BACKEND_AUTHENTICATION,
    )

    # No exception if user does already exist (status_code 400)
    if not r.ok and r.status_code != 400:
        raise requests.HTTPError(r)
    return r.json()


def remove_user_from_repository(repository: str, username: str):
    r = requests.delete(
        config.T4C_REST_API + "/users/" + username,
        params={"repositoryName": repository},
        auth=T4C_BACKEND_AUTHENTICATION,
    )
    # No exception if user does not exist (status_code 404)
    if not r.ok and r.status_code != 404:
        raise requests.HTTPError(r)


def update_password_of_user(repository: str, username: str, password: str):
    r = requests.put(
        config.T4C_REST_API + "/users/" + username,
        params={"repositoryName": repository},
        json={
            "id": username,
            "isAdmin": False,
            "password": password,
        },
        auth=T4C_BACKEND_AUTHENTICATION,
    )
    r.raise_for_status()
    return r.json()


def get_repositories() -> t.List[str]:
    r = requests.get(
        config.T4C_REST_API + "/repositories", auth=T4C_BACKEND_AUTHENTICATION
    )
    r.raise_for_status()

    return [repo["name"] for repo in r.json()["repositories"]]


def create_repository(name: str) -> None:
    r = requests.post(
        config.T4C_REST_API + "/repositories",
        json={
            "repositoryName": name,
            "authenticationType": "FILE",
            "authenticationData": {
                "users": [{"login": "admin", "password": generate_password()}]
            },
            "datasourceType": "H2_EMBEDDED",
        },
        auth=T4C_BACKEND_AUTHENTICATION,
    )
    r.raise_for_status()
