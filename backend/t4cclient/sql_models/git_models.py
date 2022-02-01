from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from t4cclient.core.database import Base


class DatabaseGitModel(Base):
    __tablename__ = "git_models"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    path = Column(String)
    entrypoint = Column(String)
    revision = Column(String)
    primary = Column(Boolean)
    repository_name = Column(
        String, ForeignKey("repositories.name", ondelete="CASCADE")
    )
    repository = relationship("DatabaseRepository", back_populates="git_models")
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    project = relationship("DatabaseProject", back_populates="git_models")
    jenkins_job = relationship(
        "DatabaseJenkinsPipeline",
        cascade="all, delete-orphan",
        back_populates="git_model",
        passive_deletes=True,
    )
