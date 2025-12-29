from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
from app.database import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dj_id = Column(Integer, ForeignKey("djs.id", ondelete="CASCADE"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    booking_count = Column(Integer, default=0)
    
    # Relationships
    dj = relationship("DJ", back_populates="sessions")
    venue = relationship("Venue", back_populates="sessions")
    bookings = relationship("Booking", back_populates="session")
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def remaining_minutes(self):
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds() / 60)