# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import yaml

from capellacollab.configuration.app import config
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models

from . import interface

log = logging.getLogger(__name__)


class LogCollectorIntegration(interface.HookRegistration):
    _loki_enabled: bool = config.k8s.promtail.loki_enabled

    def configuration_hook(self, request: interface.ConfigurationHookRequest):
        if not self._log_collection_enabled(request.tool):
            return interface.ConfigurationHookResult()

        return interface.ConfigurationHookResult(
            volumes=[self._get_logs_volume(session_id=request.session_id)]
        )

    @classmethod
    def _get_logs_volume(
        cls, session_id: str
    ) -> operators_models.PersistentVolume:
        return operators_models.PersistentVolume(
            name="logs",
            read_only=False,
            container_path=pathlib.PurePosixPath("/var/log/session"),
            volume_name=f"{config.k8s.release_name}-session-logs",
            sub_path=session_id,
        )

    def post_session_creation_hook(
        self,
        request: interface.PostSessionCreationHookRequest,
    ) -> interface.PostSessionCreationHookResult:
        if not self._log_collection_enabled(request.db_session.tool):
            return interface.PostSessionCreationHookResult()

        request.operator.create_configmap(
            name=request.db_session.id,
            data=self._promtail_configuration(
                session_id=request.session_id,
                username=request.user.name,
                session_type=request.db_session.type.value,
                tool=request.db_session.tool,
                version=request.db_session.version,
                connection_method=request.connection_method,
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
                sub_path=None,
            ),
            self._get_logs_volume(session_id=request.db_session.id),
        ]

        request.operator.create_sidecar_pod(
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
        if not self._log_collection_enabled(request.session.tool):
            return interface.PostSessionCreationHookResult()

        request.operator.delete_config_map(name=request.session.id)
        request.operator.delete_pod(name=f"{request.session.id}-promtail")

        return interface.PreSessionTerminationHookResult()

    def _log_collection_enabled(self, tool: tools_models.DatabaseTool) -> bool:
        return self._loki_enabled and tool.config.monitoring.logging.enabled

    @classmethod
    def _promtail_configuration(
        cls,
        session_id: str,
        username: str,
        session_type: str,
        tool: tools_models.DatabaseTool,
        version: tools_models.DatabaseVersion,
        connection_method: tools_models.ToolSessionConnectionMethod,
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
                        "filename": "/var/log/session/.positions.yaml"
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
                                    "labels": {
                                        "username": username,
                                        "session_type": session_type,
                                        "session_id": session_id,
                                        "tool_id": tool.id,
                                        "version_id": version.id,
                                        "connection_method_id": connection_method.id,
                                        "__path__": "/var/log/session/**/*.log",
                                    },
                                }
                            ],
                        }
                    ],
                }
            )
        }
