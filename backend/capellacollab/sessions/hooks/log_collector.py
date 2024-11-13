# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import yaml

from capellacollab.config import config
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import models as operators_models
from capellacollab.users.workspaces import crud as users_workspaces_crud

from . import interface

log = logging.getLogger(__name__)


class LogCollectorIntegration(interface.HookRegistration):
    _loki_enabled: bool = config.k8s.promtail.loki_enabled

    def post_session_creation_hook(
        self,
        request: interface.PostSessionCreationHookRequest,
    ) -> interface.PostSessionCreationHookResult:
        if (
            not self._loki_enabled
            or request.db_session.type == sessions_models.SessionType.READONLY
        ):
            return interface.PostSessionCreationHookResult()

        workspaces = users_workspaces_crud.get_workspaces_for_user(
            request.db, request.user
        )
        if not workspaces:
            return interface.PostSessionCreationHookResult()

        request.operator._create_configmap(
            name=request.db_session.id,
            data=self._promtail_configuration(
                username=request.user.name,
                session_type=request.db_session.type.value,
                tool_name=request.db_session.tool.name,
                version_name=request.db_session.version.name,
            ),
        )

        labels: dict[str, str] = {
            "capellacollab/workload": "session-sidecar",
            "capellacollab/session-id": request.db_session.id,
            "capellacollab/owner-id": str(request.user.id),
        }

        volumes = [
            operators_models.ConfigMapReferenceVolume(
                name="prom-config",
                read_only=True,
                container_path=pathlib.PurePosixPath("/etc/promtail"),
                config_map_name=request.db_session.id,
                optional=False,
            ),
            operators_models.PersistentVolume(
                name="workspace",
                read_only=False,
                container_path=pathlib.PurePosixPath("/var/log/promtail"),
                volume_name=workspaces[0].pvc_name,
            ),
        ]

        request.operator._create_sidecar_pod(
            image=f"{config.docker.external_registry}/grafana/promtail",
            name=f"{request.db_session.id}-promtail",
            labels=labels,
            args=[
                "--config.file=/etc/promtail/promtail.yaml",
                "-log-config-reverse-order",
            ],
            volumes=volumes,
        )

        return interface.PostSessionCreationHookResult()

    def pre_session_termination_hook(
        self,
        request: interface.PreSessionTerminationHookRequest,
    ) -> interface.PreSessionTerminationHookResult:
        if (
            not self._loki_enabled
            or request.session.type == sessions_models.SessionType.READONLY
        ):
            return interface.PostSessionCreationHookResult()

        request.operator._delete_config_map(name=request.session.id)
        request.operator._delete_pod(name=f"{request.session.id}-promtail")

        return interface.PreSessionTerminationHookResult()

    @classmethod
    def _promtail_configuration(
        cls,
        username: str,
        session_type: str,
        tool_name: str,
        version_name: str,
    ) -> dict:
        cfg = config.k8s.promtail

        return {
            "promtail.yaml": yaml.dump(
                {
                    "server": {
                        "http_listen_port": cfg.server_port,
                    },
                    "clients": [
                        {
                            "url": cfg.loki_url + "/push",
                            "basic_auth": {
                                "username": cfg.loki_username,
                                "password": cfg.loki_password,
                            },
                        }
                    ],
                    "positions": {
                        "filename": "/var/log/promtail/positions.yaml"
                    },
                    "scrape_configs": [
                        {
                            "job_name": "system",
                            "pipeline_stages": [
                                {
                                    "multiline": {
                                        "firstline": "^[^\t]",
                                    },
                                }
                            ],
                            "static_configs": [
                                {
                                    "targets": ["localhost"],
                                    "labels": {
                                        "username": username,
                                        "session_type": session_type,
                                        "tool": tool_name,
                                        "version": version_name,
                                        "__path__": "/var/log/promtail/**/*.log",
                                    },
                                }
                            ],
                        }
                    ],
                }
            )
        }
