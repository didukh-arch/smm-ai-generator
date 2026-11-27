from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    plan = Column(String(50), default="free", nullable=False)  # free, pro, business
    plan_end_date = Column(Date, nullable=True)  # Дата завершення платного абонемента
    daily_used = Column(Integer, default=0, nullable=False)
    last_usage_date = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    scenarios = relationship("ScenarioDB", back_populates="owner", cascade="all, delete-orphan")


class ScenarioDB(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    content_type = Column(String(50), default="scenario", nullable=False)
    option_label = Column(String(100), default="20 с", nullable=False)
    tone = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    notes = Column(Text, default="", nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("UserDB", back_populates="scenarios")



class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan = Column(String, nullable=False)          # 'pro' або 'business'
    amount = Column(Float, nullable=False)         # 99.00 або 199.00
    card_last4 = Column(String(4), nullable=False) # останні 4 цифри картки (напр. '7788')
    status = Column(String, default="success")     # 'success'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")