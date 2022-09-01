# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter
from pydantic import BaseModel

import t4cclient


class Metadata(BaseModel):
    version: str

    class Config:
        orm_mode = True


router = APIRouter()


@router.get(
    "/metadata",
    response_model=Metadata,
)
def get_metadata():
    return Metadata(version=t4cclient.__version__)
