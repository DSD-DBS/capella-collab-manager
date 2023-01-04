# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import ProjectRoleVerification
from capellacollab.core.database import Base, get_db
from capellacollab.projects.users.models import ProjectUserRole

from .. import crud
from ..injectables import get_existing_capella_model
from ..models import DatabaseCapellaModel
from .models import ToolModelRestrictions


def get_model_restrictions(
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
) -> ToolModelRestrictions:
    return model.restrictions
