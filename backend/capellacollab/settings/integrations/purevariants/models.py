# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel
from sqlalchemy import Column, String

from capellacollab.core.database import Base


class DatabasePureVariantsLicenses(Base):
    __tablename__ = "pure_variants_license"

    value = Column(String, primary_key=True)


class PureVariantsLicenses(BaseModel):
    value: str

    class Config:
        orm_mode = True
