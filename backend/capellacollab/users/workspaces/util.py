# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from capellacollab.core import exceptions as core_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.users import models as users_models

from . import crud, models


def delete_all_workspaces_of_user(
    db: orm.Session, user: users_models.DatabaseUser
):
    for workspace in crud.get_workspaces_for_user(db=db, user=user):
        delete_workspace(db, workspace)


def delete_workspace(db: orm.Session, workspace: models.DatabaseWorkspace):
    persistent_sessions_of_user = [
        session
        for session in workspace.user.sessions
        if session.type == sessions_models.SessionType.PERSISTENT
    ]
    if persistent_sessions_of_user:
        raise core_exceptions.ExistingDependenciesError(
            workspace.pvc_name,
            "workspace",
            [
                f"Session {session.id}"
                for session in persistent_sessions_of_user
            ],
        )
    operators.get_operator().delete_persistent_volume(workspace.pvc_name)
    crud.delete_workspace(db, workspace)
