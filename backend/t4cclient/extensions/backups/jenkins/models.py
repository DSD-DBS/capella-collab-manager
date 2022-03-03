from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from t4cclient.core.database import Base


class DatabaseJenkinsPipeline(Base):
    __tablename__ = "jenkins"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    git_model_id = Column(
        Integer, ForeignKey("git_models.id", ondelete="CASCADE"), primary_key=True
    )
    git_model = relationship(
        "DatabaseGitModel",
        back_populates="jenkins_job",
    )
