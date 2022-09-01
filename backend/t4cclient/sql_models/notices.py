# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Enum, Integer, String

from t4cclient.core.database import Base
from t4cclient.schemas.notices import NoticeLevel


class DatabaseNotice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(String)
    level = Column(Enum(NoticeLevel))
    scope = Column(String)
