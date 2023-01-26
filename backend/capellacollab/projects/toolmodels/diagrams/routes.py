# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime

import fastapi
import requests
from fastapi import responses

from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.projects.toolmodels.diagrams import models
from capellacollab.projects.users.models import ProjectUserRole

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            ProjectRoleVerification(required_role=ProjectUserRole.USER)
        )
    ],
)


@router.get("", response_model=models.DiagramCacheMetadata)
def get_diagram_metadata():
    response = requests.get(
        "https://gitlab.com/api/v4/projects/-/jobs/artifacts/diagram_cache/raw/artifacts/diagrams/index.json?job=capella_diagram_cache_svg",
        headers={"PRIVATE-TOKEN": "-"},
        timeout=2,
    )
    return {"diagrams": response.json(), "last_updated": datetime.now()}


@router.get("/{diagram_uuid}", response_class=responses.Response)
def get_diagram(diagram_uuid: str):
    response = requests.get(
        f"https://gitlab.com/api/v4/projects/-/jobs/artifacts/diagram_cache/raw/artifacts/diagrams/{diagram_uuid}.svg?job=capella_diagram_cache_svg",
        headers={"PRIVATE-TOKEN": "-"},
        timeout=2,
    )
    response.raise_for_status()
    return responses.Response(
        content=response.content,
        media_type="image/svg+xml",
    )
