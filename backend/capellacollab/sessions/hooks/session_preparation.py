# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import models as operators_models

from . import interface


class GitRepositoryCloningHook(interface.HookRegistration):
    """Creates a volume that is shared between the actual container and the session preparation.

    The volume is used to clone Git repositories as preparation for the session.
    """

    def configuration_hook(
        self,
        request: interface.ConfigurationHookRequest,
    ) -> interface.ConfigurationHookResult:
        if request.session_type != sessions_models.SessionType.READONLY:
            return interface.ConfigurationHookResult()

        shared_model_volume = operators_models.EmptyVolume(
            name=f"{request.session_id}-models",
            container_path=pathlib.PurePosixPath(
                request.tool.config.provisioning.directory
            ),
            read_only=False,
            sub_path=None,
        )

        return interface.ConfigurationHookResult(
            volumes=[shared_model_volume],
            init_volumes=[shared_model_volume],
        )
