from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from t4cclient.core.database import Base
from t4cclient.schemas.repositories import RepositoryUserPermission, RepositoryUserRole


class RepositoryUserAssociation(Base):
    __tablename__ = "repository_user_association"

    username = Column(ForeignKey("users.name"), primary_key=True)
    repository_name = Column(ForeignKey("repositories.name"), primary_key=True)
    user = relationship("DatabaseUser", back_populates="repositories")
    repository = relationship("DatabaseRepository", back_populates="users")
    permission = Column(Enum(RepositoryUserPermission), nullable=False)
    role = Column(Enum(RepositoryUserRole))


class DatabaseRepository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship(
        "RepositoryUserAssociation",
        back_populates="repository",
    )
    projects = relationship("DatabaseProject", back_populates="repository")
    git_models = relationship("DB_GitModel", back_populates="repository")
