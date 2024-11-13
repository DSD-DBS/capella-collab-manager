# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from . import interface


class NetworkingIntegration(interface.HookRegistration):
    """Allow sessions of the same user to talk to each other."""

    def post_session_creation_hook(
        self, request: interface.PostSessionCreationHookRequest
    ) -> interface.PostSessionCreationHookResult:
        """Allow sessions of the user to talk to each other."""

        request.operator.create_network_policy_from_pod_to_label(
            request.session_id,
            match_labels_from={
                "capellacollab/session-id": request.session_id,
                "capellacollab/workload": "session",
            },
            match_labels_to={
                "capellacollab/owner-id": str(request.user.id),
                "capellacollab/workload": "session",
            },
        )

        return interface.PostSessionCreationHookResult()

    def pre_session_termination_hook(
        self, request: interface.PreSessionTerminationHookRequest
    ):
        request.operator.delete_network_policy(request.session.id)
