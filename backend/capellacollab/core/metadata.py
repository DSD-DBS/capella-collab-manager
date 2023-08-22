# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pydantic

import capellacollab


class Metadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    version: str


router = fastapi.APIRouter()


@router.get(
    "/metadata",
    response_model=Metadata,
)
def get_metadata():
    return Metadata(version=capellacollab.__version__)
