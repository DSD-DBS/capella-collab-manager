# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import models as operators_models

from . import interface


class ReadOnlyWorkspaceHook(interface.HookRegistration):
    """Mounts an empty workspace to the container for read-only sessions."""

    def configuration_hook(  # type: ignore
        self,
        session_type: sessions_models.SessionType,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        if session_type != sessions_models.SessionType.READONLY:
            # Configuration for persistent workspace sessions happens in the PersistentWorkspaceHook.
            return interface.ConfigurationHookResult()

        return interface.ConfigurationHookResult(
            volumes=[
                operators_models.EmptyVolume(
                    name="workspace",
                    read_only=False,
                    container_path=pathlib.PurePosixPath("/workspace"),
                )
            ],
        )
