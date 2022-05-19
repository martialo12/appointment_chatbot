"""Models chatbot module."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from app.db.database import Base


class GoogleCredentials(Base):
    __tablename__ = "google_credentials"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    timezone = Column(String, nullable=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return (
            f"<GoogleCredentials(id='{self.id}', "
            f"name='{self.name}', "
            f"email='{self.email}', "
            f"access_token='{self.access_token}', "
            f"refresh_token='{self.refresh_token}'>"
        )
