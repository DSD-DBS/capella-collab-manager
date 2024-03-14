# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import typing as t
import uuid

import requests
from requests import auth as requests_auth
from requests import exceptions as requests_exceptions

from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import k8s
from capellacollab.tools import models as tools_models

from . import interface

log = logging.getLogger(__name__)


class GuacamoleError(Exception):
    pass


class GuacamoleConfig(t.TypedDict):
    guacamole_username: str
    guacamole_password: str
    guacamole_connection_id: str


class GuacamoleIntegration(interface.HookRegistration):
    _baseURI = config["extensions"]["guacamole"]["baseURI"]
    _prefix = f"{_baseURI}/api/session/data/postgresql"
    _headers = {"Content-Type": "application/x-www-form-urlencoded"}
    _proxies = {
        "http": None,
        "https": None,
    }

    def post_session_creation_hook(  # type: ignore[override]
        self,
        session: k8s.Session,
        db_session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> interface.PostSessionCreationHookResult:
        if connection_method.type != "guacamole":
            return interface.PostSessionCreationHookResult()

        guacamole_username = credentials.generate_password()
        guacamole_password = credentials.generate_password(length=64)

        guacamole_token = self._get_admin_token()
        self._create_user(
            guacamole_token, guacamole_username, guacamole_password
        )

        guacamole_identifier = self._create_connection(
            guacamole_token,
            db_session.environment["CAPELLACOLLAB_SESSION_TOKEN"],
            session["host"],
            session["port"],
        )["identifier"]

        self._assign_user_to_connection(
            guacamole_token, guacamole_username, guacamole_identifier
        )

        guacamole_config: GuacamoleConfig = {
            "guacamole_username": guacamole_username,
            "guacamole_password": guacamole_password,
            "guacamole_connection_id": guacamole_identifier,
        }

        return interface.PostSessionCreationHookResult(
            config=guacamole_config,
        )

    def session_connection_hook(  # type: ignore[override]
        self,
        db_session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> interface.SessionConnectionHookResult:
        if connection_method.type != "guacamole":
            return interface.SessionConnectionHookResult()

        session_config = db_session.config

        if not session_config or not session_config.get("guacamole_username"):
            return interface.SessionConnectionHookResult()

        token = self._get_token(
            session_config["guacamole_username"],
            session_config["guacamole_password"],
        )
        return interface.SessionConnectionHookResult(
            local_storage={"GUAC_AUTH": json.dumps(token)},
            redirect_url=config["extensions"]["guacamole"]["publicURI"]
            + "/#/",
        )

    def pre_session_termination_hook(  # type: ignore[override]
        self,
        session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        **kwargs,
    ) -> interface.PreSessionTerminationHookResult:
        if connection_method.type != "guacamole":
            return interface.SessionConnectionHookResult()

        session_config = session.config

        if session_config and session_config.get("guacamole_username"):
            guacamole_token = self._get_admin_token()
            self._delete_user(
                guacamole_token, session_config["guacamole_username"]
            )
            self._delete_connection(
                guacamole_token, session_config["guacamole_connection_id"]
            )
        return interface.PreSessionTerminationHookResult()

    @classmethod
    def _get_admin_token(cls) -> str:
        r = requests.post(
            f"{cls._baseURI}/api/tokens",
            auth=requests_auth.HTTPBasicAuth(
                config["extensions"]["guacamole"]["username"],
                config["extensions"]["guacamole"]["password"],
            ),
            headers=cls._headers,
            timeout=config["requests"]["timeout"],
            proxies=cls._proxies,
        )
        try:
            r.raise_for_status()
        except requests_exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 404:
                raise GuacamoleError(
                    "Could not create an admin token. Please make sure that your Guacamole instance is running."
                ) from e
            elif status == 500:
                raise GuacamoleError(
                    "Could not create an admin token. Please make sure that your Guacamole database is initialized properly."
                ) from e
            else:
                raise e
        return r.json()["authToken"]

    @classmethod
    def _get_token(cls, username: str, password: str) -> str:
        r = requests.post(
            f"{cls._baseURI}/api/tokens",
            auth=requests_auth.HTTPBasicAuth(username, password),
            headers=cls._headers,
            timeout=config["requests"]["timeout"],
            proxies=cls._proxies,
        )
        r.raise_for_status()
        return r.json()

    @classmethod
    def _create_user(
        cls,
        token: str,
        username: str = credentials.generate_password(10),
        password: str = credentials.generate_password(128),
    ) -> None:
        r = requests.post(
            f"{cls._prefix}/users?token={token}",
            json={
                "username": username,
                "password": password,
                "attributes": {},
            },
            timeout=config["requests"]["timeout"],
            proxies=cls._proxies,
        )
        r.raise_for_status()
        return r.json()

    @classmethod
    def _assign_user_to_connection(
        cls, token: str, username: str, connection_id: str
    ):
        r = requests.patch(
            f"{cls._prefix}/users/{username}/permissions?token={token}",
            json=[
                {
                    "op": "add",
                    "path": f"/connectionPermissions/{connection_id}",
                    "value": "READ",
                }
            ],
            timeout=config["requests"]["timeout"],
            proxies=cls._proxies,
        )
        r.raise_for_status()

    @classmethod
    def _delete_user(cls, token: str, username: str):
        r = requests.delete(
            f"{cls._prefix}/users/{username}?token={token}",
            timeout=config["requests"]["timeout"],
            proxies=cls._proxies,
        )
        try:
            r.raise_for_status()
        except requests_exceptions.HTTPError as e:
            if e.response.status_code == 404:
                log.warning(
                    "User %s does not exist in Guacamole. Skipping deletion.",
                    username,
                )
            else:
                raise e

    @classmethod
    def _delete_connection(cls, token: str, connection_name: str):
        r = requests.delete(
            f"{cls._prefix}/connections/{connection_name}?token={token}",
            timeout=config["requests"]["timeout"],
            proxies=cls._proxies,
        )
        try:
            r.raise_for_status()
        except requests_exceptions.HTTPError as e:
            if e.response.status_code == 404:
                log.warning(
                    "Connection %s does not exist in Guacamole. Skipping deletion.",
                    connection_name,
                )
            else:
                raise e

    @classmethod
    def _create_connection(
        cls,
        token: str,
        rdp_password: str,
        rdp_host: str,
        rdp_port: int,
    ):
        r = requests.post(
            f"{cls._prefix}/connections?token={token}",
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
            proxies=cls._proxies,
        )

        r.raise_for_status()
        return r.json()

    @classmethod
    def validate_guacamole(cls) -> bool:
        try:
            cls._get_admin_token()
            return True
        except BaseException:
            return False
