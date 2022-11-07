# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from capellacollab.core.database import Base


class BackupSettings(BaseModel):
    docker_image: str

    class Config:
        orm_mode = True


class DatabaseBackupSettings(Base):
    __tablename__ = "settings_backups"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    docker_image = Column(String)
