# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators.k8s import KubernetesOperator
from capellacollab.sessions.schema import WorkspaceType
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as t4c_repositories_crud,
)
from capellacollab.settings.modelsources.t4c.repositories.interface import (
    remove_user_from_repository,
)

from . import crud

log = logging.getLogger(__name__)


def terminate_session(
    db: Session, session: DatabaseSession, operator: KubernetesOperator
):
    if (
        session.tool.integrations.t4c
        and session.type == WorkspaceType.PERSISTENT
    ):
        revoke_session_tokens(db, session)

    crud.delete_session(db, session)
    operator.kill_session(session.id)


def revoke_session_tokens(db: Session, session: DatabaseSession):
    for repository in t4c_repositories_crud.get_user_t4c_repositories(
        db, session.version.name, session.owner
    ):
        try:
            remove_user_from_repository(
                repository.instance, repository.name, session.owner.name
            )
        except RequestException:
            log.exception(
                "Could not delete user from repository '%s' of instance '%s'. Please delete the user manually.",
                exc_info=True,
            )
