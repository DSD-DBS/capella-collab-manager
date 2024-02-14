# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.sessions import operators

from .. import models as projects_models
from . import models


def create_shared_workspace(
    name: str,
    project: projects_models.DatabaseProject,
    model: models.DatabaseToolModel,
    size: str,
):
    operators.get_operator().create_persistent_volume(
        name="shared-workspace-" + name,
        size=size,
        labels={
            "capellacollab/project_slug": project.slug,
            "capellacollab/project_id": str(project.id),
            "capellacollab/model_slug": model.slug,
            "capellacollab/model_id": str(model.id),
        },
    )


def delete_shared_workspace(name: str):
    operators.get_operator().delete_persistent_volume(
        name="shared-workspace-" + name
    )
