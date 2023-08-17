# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from .operators import k8s


def _get_volume_name(username: str) -> str:
    return "persistent-session-" + _normalize_username(username)


def _normalize_username(username: str) -> str:
    return username.replace("@", "-at-").replace(".", "-dot-").lower()


def create_persistent_workspace(
    operator: k8s.KubernetesOperator, username: str
) -> str:
    persistent_workspace_name = _get_volume_name(username)
    operator.create_persistent_volume(
        _get_volume_name(username),
        "20Gi",
        labels={
            "capellacollab/username": _normalize_username(username),
        },
    )
    return persistent_workspace_name
