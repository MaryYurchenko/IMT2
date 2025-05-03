from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    measurements = relationship("Measurement", back_populates="user")


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight = Column(Float)  # в кг
    height = Column(Float)  # в см
    measured_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="measurements")


class BMICategory(Base):
    __tablename__ = "bmi_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    min_value = Column(Float)
    max_value = Column(Float)
    description = Column(Text)
    recommendations = Column(Text)