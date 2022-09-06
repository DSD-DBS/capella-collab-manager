# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

# 1st party:
from capellacollab.core.database import Base


class WorkspaceDockerimages(BaseModel):
    persistent: str
    readonly: str

    class Config:
        orm_mode = True


class Dockerimages(BaseModel):
    id: int
    environment: str
    workspaces: WorkspaceDockerimages

    class Config:
        orm_mode = True


class DB_Dockerimages(Base):
    __tablename__ = "config_dockerimages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    environment = Column(String)
    persistentworkspace = Column(String)
    readonlyworkspace = Column(String)

    def toPydantic(self):
        return Dockerimages(
            id=self.id,
            environment=self.environment,
            workspaces=WorkspaceDockerimages(
                persistent=self.persistentworkspace,
                readonly=self.readonlyworkspace,
            ),
        )
