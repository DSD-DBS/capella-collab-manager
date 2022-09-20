# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import pathlib
import shutil
import typing as t

import docker

from capellacollab.config import config
from capellacollab.core.operators.abc import Operator

log = logging.getLogger(__name__)
cfg = config["operators"]["docker"]


class DockerOperator(Operator):
    def __init__(self):
        self.client = docker.from_env()
        log.warning(
            "The DockerOperator is currently no longer fully supported. It is not recommended to use it."
        )

    def start_persistent_session(
        self,
        username: str,
        password: str,
        repositories: t.List[str],
    ) -> t.Dict[str, t.Any]:
        path_to_workspace = pathlib.Path("/workspaces", username)
        if not path_to_workspace.exists():
            path_to_workspace.mkdir(mode=0o755)
            shutil.chown(path_to_workspace, user=1001380000)

        con = self.client.containers.run(
            image=config["docker"]["images"]["workspaces"]["persistent"],
            volumes={
                cfg["mountVolume"]
                + f"/workspaces/{username}": {
                    "bind": "/workspace",
                    "mode": "rw",
                }
            },
            ports={"3389/tcp": cfg["portRange"]},
            environment={
                "RMT_PASSWORD": password,
                "T4C_REPOSITORIES": ",".join(repositories),
                "T4C_HOST": cfg["containerHost"],
            },
            detach=True,
        )
        return self.__export_attrs_from_container(
            self.client.containers.get(con.attrs["Id"])
        )

    def start_readonly_session(
        self,
        password: str,
        git_url: str,
        git_revision: str,
        entrypoint: str,
        git_username: str,
        git_password: str,
    ) -> t.Dict[str, t.Any]:
        con = self.client.containers.run(
            image=config["docker"]["images"]["workspaces"]["readonly"],
            ports={"3389/tcp": cfg["portRange"]},
            environment={
                "GIT_USERNAME": git_username,
                "GIT_PASSWORD": git_password,
                "GIT_URL": git_url,
                "GIT_REVISION": git_revision,
                "GIT_ENTRYPOINT": entrypoint,
                "RMT_PASSWORD": password,
            },
            detach=True,
        )
        return self.__export_attrs_from_container(
            self.client.containers.get(con.attrs["Id"])
        )

    def get_session_state(self, id: str):
        try:
            return self.client.containers.get(id).attrs["State"]["Status"]
        except docker.errors.NotFound:
            return "removed"

    def kill_session(self, id: str):
        return self.client.containers.get(id).stop()

    def __export_attrs_from_container(self, container):
        return {
            "id": container.attrs["Id"],
            "ports": set(
                [
                    port["HostPort"]
                    for port in container.attrs["NetworkSettings"]
                    .get("Ports", {})
                    .get("3389/tcp", [])
                ]
            ),
            "created_at": container.attrs["Created"],
            "host": cfg["containerHost"],
        }
