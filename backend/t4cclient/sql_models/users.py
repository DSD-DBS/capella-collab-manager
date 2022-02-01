from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from t4cclient.core.database import Base
from t4cclient.schemas.repositories.users import Role


class DatabaseUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    role = Column(Enum(Role))
    repositories = relationship(
        "RepositoryUserAssociation",
        back_populates="user",
    )
    sessions = relationship(
        "DatabaseSession",
        back_populates="owner",
    )
