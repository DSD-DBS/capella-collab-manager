# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib
import typing as t

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.operators import models as operators_models
from capellacollab.settings.integrations.purevariants import (
    crud as purevariants_crud,
)
from capellacollab.users import models as users_models

from . import interface

log = logging.getLogger(__name__)


class PureVariantsConfigEnvironment(t.TypedDict):
    PURE_VARIANTS_LICENSE_SERVER: t.NotRequired[str]


class PureVariantsIntegration(interface.HookRegistration):
    def configuration_hook(  # type: ignore
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        session_type: sessions_models.SessionType,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        if session_type == sessions_models.SessionType.READONLY:
            # Skip read-only sessions, no pure::variants integration supported.
            return interface.ConfigurationHookResult()

        if (
            not self._user_has_project_with_pure_variants_model(user)
            and user.role == users_models.Role.USER
        ):
            warnings = [
                core_models.Message(
                    err_code="PV_MODEL_NOT_FOUND",
                    reason=(
                        "You are trying to create a persistent session with a pure::variants integration.",
                        "We were not able to find a model with a pure::variants integration.",
                        "Your session will not be connected to the pure::variants license server.",
                    ),
                )
            ]

            return interface.ConfigurationHookResult(
                warnings=warnings,
            )

        pv_license = purevariants_crud.get_pure_variants_configuration(db)
        if not pv_license or pv_license.license_server_url is None:
            warnings = [
                core_models.Message(
                    err_code="PV_LICENSE_SERVER_NOT_CONFIGURED",
                    reason=(
                        "You are trying to create a persistent session with a pure::variants integration.",
                        "We were not able to find a valid license server URL in our database.",
                        "Your session will not be connected to the pure::variants license server.",
                    ),
                )
            ]

            return interface.ConfigurationHookResult(
                warnings=warnings,
            )

        pure_variants_environment: PureVariantsConfigEnvironment = {
            "PURE_VARIANTS_LICENSE_SERVER": pv_license.license_server_url,
        }

        pure_variants_secret = operators_models.SecretReferenceVolume(
            name="pure-variants",
            read_only=True,
            container_path=pathlib.PurePosixPath("/inputs/pure-variants"),
            secret_name="pure-variants",
            optional=True,
        )

        return interface.ConfigurationHookResult(
            environment=pure_variants_environment,
            volumes=[pure_variants_secret],
        )

    def _model_allows_pure_variants(
        self,
        model: toolmodels_models.DatabaseToolModel,
    ):
        return model.restrictions and model.restrictions.allow_pure_variants

    def _user_has_project_with_pure_variants_model(
        self,
        user: users_models.DatabaseUser,
    ):
        return any(
            self._model_allows_pure_variants(model)
            for association in user.projects
            for model in association.project.models
        )
