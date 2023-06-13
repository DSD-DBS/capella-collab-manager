# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import requests
from sqlalchemy import orm

from capellacollab.sessions.operators import k8s
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as t4c_repositories_crud,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    interface as settings_t4c_repositories_interface,
)

from . import crud, models

log = logging.getLogger(__name__)


def terminate_session(
    db: orm.Session,
    session: models.DatabaseSession,
    operator: k8s.KubernetesOperator,
):
    if (
        session.tool.integrations.t4c
        and session.type == models.WorkspaceType.PERSISTENT
    ):
        revoke_session_tokens(db, session)

    crud.delete_session(db, session)
    operator.kill_session(session.id)


def revoke_session_tokens(db: orm.Session, session: models.DatabaseSession):
    for repository in t4c_repositories_crud.get_user_t4c_repositories(
        db, session.version.name, session.owner
    ):
        try:
            settings_t4c_repositories_interface.remove_user_from_repository(
                repository.instance, repository.name, session.owner.name
            )
        except requests.RequestException:
            log.exception(
                "Could not delete user from repository '%s' of instance '%s'. Please delete the user manually.",
                exc_info=True,
            )
