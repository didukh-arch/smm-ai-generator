from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scenarios = relationship("ScenarioDB", back_populates="author")


class PlatformDB(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  

    scenarios = relationship("ScenarioDB", back_populates="platform")


class ScenarioDB(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    tone = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=True)

    author = relationship("UserDB", back_populates="scenarios")
    platform = relationship("PlatformDB", back_populates="scenarios")