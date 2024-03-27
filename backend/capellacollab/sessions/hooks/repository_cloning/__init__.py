# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

from capellacollab.config import config as cfg
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.users import models as users_models

from .. import interface


class PersistentWorkspacEnvironment(t.TypedDict):
    pass


class GitRepositoryCloningHook(interface.HookRegistration):
    """Clones are Git repository before read-only session startup in the container."""

    def configuration_hook(  # type: ignore
        self,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        session_type: sessions_models.SessionType,
        session_id: str,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        if session_type != sessions_models.SessionType.READONLY:
            return interface.ConfigurationHookResult()

        shared_model_volume = operators_models.EmptyVolume(
            name=f"{session_id}-shared-models",
            container_path=pathlib.PurePosixPath("/shared_models"),
            read_only=False,
        )

        return interface.ConfigurationHookResult(
            volumes=[shared_model_volume],
            init_containers=[
                operators_models.Container(
                    image=cfg.docker.external_registry,
                    volumes=[shared_model_volume],
                )
            ],
        )
