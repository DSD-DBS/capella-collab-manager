# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators.k8s import KubernetesOperator
from capellacollab.sessions.schema import WorkspaceType
from capellacollab.settings.modelsources.t4c.repositories.crud import (
    get_user_t4c_repositories,
)
from capellacollab.settings.modelsources.t4c.repositories.interface import (
    remove_user_from_repository,
)

from . import crud

log = logging.getLogger(__name__)


def terminate_session(
    db_session: Session, session: DatabaseSession, operator: KubernetesOperator
):
    if (
        session.tool.integrations.t4c
        and session.type == WorkspaceType.PERSISTENT
    ):
        revoke_session_tokens(db_session, session)

    crud.delete_session(db_session, session)
    operator.kill_session(session.id)


def revoke_session_tokens(db_session: Session, session: DatabaseSession):
    for repository in get_user_t4c_repositories(
        db_session, session.tool, session.version, session.owner
    ):
        try:
            remove_user_from_repository(
                repository.instance,
                repository.name,
                username=session.owner.name,
            )
        except RequestException:
            log.exception(
                "Could not delete user from repository '%s' of instance '%s'. Please delete the user manually.",
                exc_info=True,
            )
