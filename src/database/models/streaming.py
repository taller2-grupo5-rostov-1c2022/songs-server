from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from src.database.access import Base


class StreamingModel(Base):
    __tablename__ = "streamings"

    listener_token = Column(String, primary_key=True)
    artist_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    artist = relationship("UserModel", back_populates="streaming")

    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)
