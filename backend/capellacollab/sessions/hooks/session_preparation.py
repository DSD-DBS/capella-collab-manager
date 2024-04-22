# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models

from . import interface


class PersistentWorkspacEnvironment(t.TypedDict):
    pass


class GitRepositoryCloningHook(interface.HookRegistration):
    """Creates a volume that is shared between the actual container and the session preparation.

    The volume is used to clone Git repositories as preparation for the session.
    """

    def configuration_hook(  # type: ignore
        self,
        session_type: sessions_models.SessionType,
        session_id: str,
        tool: tools_models.DatabaseTool,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        if session_type != sessions_models.SessionType.READONLY:
            return interface.ConfigurationHookResult()

        shared_model_volume = operators_models.EmptyVolume(
            name=f"{session_id}-models",
            container_path=pathlib.PurePosixPath(
                tool.config.provisioning.directory
            ),
            read_only=False,
        )

        return interface.ConfigurationHookResult(
            volumes=[shared_model_volume],
            init_volumes=[shared_model_volume],
        )
