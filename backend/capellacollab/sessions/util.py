# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from sqlalchemy import orm

from capellacollab.sessions.operators import k8s

from . import crud, hooks, models

log = logging.getLogger(__name__)


def terminate_session(
    db: orm.Session,
    session: models.DatabaseSession,
    operator: k8s.KubernetesOperator,
):
    for hook in hooks.get_activated_integration_hooks(session.tool):
        hook.pre_session_termination_hook(
            db=db, session=session, operator=operator, user=session.owner
        )

    crud.delete_session(db, session)
    operator.kill_session(session.id)
