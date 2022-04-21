# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from t4cclient.core.database import Base


class CreateJenkinsJob(BaseModel):
    name: str

    class Config:
        orm_mode = True


class JenkinsRun(BaseModel):
    id: int
    result: str
    start_time: str
    logs_url: str

    class Config:
        orm_mode = True


class JenkinsPipeline(CreateJenkinsJob):
    id: int
    latest_run: t.Optional[JenkinsRun]


class DatabaseJenkinsPipeline(Base):
    __tablename__ = "jenkins"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    git_model_id = Column(
        Integer, ForeignKey("git_models.id", ondelete="CASCADE"), primary_key=True
    )
    git_model = relationship(
        "DB_GitModel",
    )
