from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=True)
    capacity = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    active = Column(Boolean, default=False, index=True)
    dj_id = Column(Integer, ForeignKey("djs.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dj = relationship("DJ", back_populates="venues")
    bookings = relationship("Booking", back_populates="venue", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="venue", cascade="all, delete-orphan")