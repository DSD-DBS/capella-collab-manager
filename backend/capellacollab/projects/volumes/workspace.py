# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.projects import models as projects_models
from capellacollab.sessions import operators


def create_shared_workspace(
    name: str,
    project: projects_models.DatabaseProject,
    size: str,
):
    operators.get_operator().create_persistent_volume(
        name="shared-workspace-" + name,
        size=size,
        labels={
            "capellacollab/project_slug": project.slug,
            "capellacollab/project_id": str(project.id),
        },
    )


def delete_shared_workspace(name: str):
    operators.get_operator().delete_persistent_volume(
        name="shared-workspace-" + name
    )
