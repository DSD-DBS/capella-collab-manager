from sqlalchemy import Column, ForeignKey, Integer
from capellacollab.core.database import Base


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    t4c_model = relationship


class GitSource(Base):
    __tablename__ = 'git_sources'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
