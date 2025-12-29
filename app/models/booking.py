from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), nullable=False)
    song = Column(String(300), nullable=False)
    key = Column(String(10), default="0")
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    venue = relationship("Venue", back_populates="bookings")
    session = relationship("Session", back_populates="bookings")