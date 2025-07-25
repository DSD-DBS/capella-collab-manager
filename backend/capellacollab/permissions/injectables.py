# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import typing as t

import fastapi

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

from . import exceptions, models


def get_scope(
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    token: t.Annotated[
        tokens_models.DatabaseUserToken | None,
        fastapi.Depends(auth_injectables.get_auth_pat),
    ],
) -> models.GlobalScopes:
    role_permissions = models.ROLE_MAPPING[user.role]

    if token:
        return token.scope & role_permissions

    return role_permissions


@dataclasses.dataclass(eq=False)
class PermissionValidation:
    required_scope: models.GlobalScopes | None
    exceptions = [exceptions.InsufficientPermissionError]

    def __call__(
        self,
        actual_scope: t.Annotated[
            models.GlobalScopes, fastapi.Depends(get_scope)
        ],
    ) -> None:
        if self.required_scope is None:
            self.required_scope = models.GlobalScopes()

        actual_scope_dump = actual_scope.model_dump()

        for scope, perms in self.required_scope:
            for perm, verbs in perms:
                for verb in verbs:
                    if verb not in actual_scope_dump[scope][perm]:
                        raise exceptions.InsufficientPermissionError(
                            f"{scope}.{perm}", verbs
                        )

    def list_repr(self) -> list[str]:
        if self.required_scope is None:
            return []

        required_permissions = []
        for scope, inner_scope in self.required_scope:
            for perms, verbs in inner_scope:
                for verb in verbs:
                    required_permissions.append(
                        f"{scope}.{perms}:{verb.lower()}"
                    )
        return required_permissions
