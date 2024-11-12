# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.sessions import operators
from capellacollab.users import models as users_models

from .. import models as sessions_models
from . import interface


class NetworkingIntegration(interface.HookRegistration):
    """Allow sessions of the same user to talk to each other."""

    def post_session_creation_hook(  # type: ignore
        self,
        session_id: str,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        **kwargs,
    ) -> interface.PostSessionCreationHookResult:
        """Allow sessions of the user to talk to each other."""

        operator.create_network_policy_from_pod_to_label(
            session_id,
            match_labels_from={
                "capellacollab/session-id": session_id,
                "capellacollab/workload": "session",
            },
            match_labels_to={
                "capellacollab/owner-id": str(user.id),
                "capellacollab/workload": "session",
            },
        )

        return interface.PostSessionCreationHookResult()

    def pre_session_termination_hook(  # type: ignore
        self,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ):
        operator.delete_network_policy(session.id)
