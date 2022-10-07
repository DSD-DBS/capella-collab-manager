# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from pydantic import BaseModel
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# required for sqlalchemy
import capellacollab.settings.modelsources.t4c.models
from capellacollab.core.database import Base


class DatabaseT4CInstance(Base):
    __tablename__ = "t4c_instances"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    version_id = Column(Integer, ForeignKey("versions.id"))
    license = Column(String)
    host = Column(String)
    port = Column(
        Integer,
        CheckConstraint("port >= 0 AND port <= 65535"),
    )
    usage_api = Column(String)
    rest_api = Column(String)
    username = Column(String)
    password = Column(String)

    version = relationship("Version")
    repositories = relationship(
        "DatabaseT4CRepository",
        back_populates="instance",
        cascade="all, delete",
    )


class T4CInstanceBase(BaseModel):
    license: str
    host: str
    port: int
    usage_api: str
    rest_api: str
    username: str

    class Config:
        orm_mode = True


class PatchT4CInstance(BaseModel):
    license: t.Optional[str]
    host: t.Optional[str]
    port: t.Optional[int]
    usage_api: t.Optional[str]
    rest_api: t.Optional[str]
    username: t.Optional[str]
    password: t.Optional[str]

    class Config:
        orm_mode = True


class T4CInstanceComplete(T4CInstanceBase):
    name: str
    version_id: int


class CreateT4CInstance(T4CInstanceComplete):
    password: str


class Version(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class T4CInstance(T4CInstanceComplete):
    id: int
    version: Version


class T4CInstanceWithRepositories(T4CInstance):
    repositories: list["T4CRepository"]

    class Config:
        orm_mode = True


class CreateT4CRepository(BaseModel):
    name: str


class T4CRepository(CreateT4CRepository):
    id: int
    instance_id: int
    instance: T4CInstance

    class Config:
        orm_mode = True


T4CInstanceWithRepositories.update_forward_refs()
