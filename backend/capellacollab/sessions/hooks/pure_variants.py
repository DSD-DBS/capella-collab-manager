# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.settings.integrations.purevariants import (
    crud as purevariants_crud,
)
from capellacollab.users import models as users_models

from . import interface

log = logging.getLogger(__name__)


class PureVariantsConfigEnvironment(t.TypedDict):
    PURE_VARIANTS_LICENSE_SERVER: str
    PURE_VARIANTS_SECRET: str


class PureVariantsIntegration(interface.HookRegistration):
    def configuration_hook(
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        **kwargs,
    ) -> tuple[PureVariantsConfigEnvironment, list[core_models.Message]]:
        warnings: list[core_models.Message] = []

        if (
            not [
                model
                for association in user.projects
                for model in association.project.models
                if model.restrictions
                and model.restrictions.allow_pure_variants
            ]
            and user.role == users_models.Role.USER
        ):
            warnings.append(
                core_models.Message(
                    reason=(
                        "You are trying to create a persistent session with a pure::variants integration.",
                        "We were not able to find a model with a pure::variants integration.",
                        "Your session will not be connected to the pure::variants license server.",
                    )
                )
            )
            return {}, warnings

        if not (
            pv_license := purevariants_crud.get_pure_variants_configuration(db)
        ):
            warnings.append(
                core_models.Message(
                    reason=(
                        "You are trying to create a persistent session with a pure::variants integration.",
                        "We were not able to find a valid license server URL in our database.",
                        "Your session will not be connected to the pure::variants license server.",
                    )
                )
            )
            return {}, warnings

        return {
            "PURE_VARIANTS_LICENSE_SERVER": pv_license.license_server_url,
            "PURE_VARIANTS_SECRET": "pure-variants",
        }, warnings
