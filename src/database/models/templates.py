from sqlalchemy import Column, Integer, String, Boolean
from src.postgres.database import Base


class ResourceModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    blocked = Column(Boolean, nullable=False, index=True)


class ResourceCreatorModel(ResourceModel):
    __abstract__ = True
    genre = Column(String, nullable=False, index=True)
