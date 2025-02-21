# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.projects import models as projects_models
from capellacollab.sessions import operators


def create_shared_workspace(
    name: str,
    project: projects_models.DatabaseProject,
    size: str,
):
    pvc_name = "shared-workspace-" + name
    operators.get_operator().create_persistent_volume(
        name=pvc_name,
        size=size,
        labels={
            "capellacollab/project_slug": project.slug,
            "capellacollab/project_id": str(project.id),
        },
    )
    return pvc_name


def delete_shared_workspace(pvc_name: str):
    operators.get_operator().delete_persistent_volume(name=pvc_name)
