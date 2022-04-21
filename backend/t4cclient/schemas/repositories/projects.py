# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from lib2to3.pytree import Base

from pydantic import BaseModel


class RepositoryProjectBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class RepositoryProject(RepositoryProjectBase):
    id: int
    repository_name: str
