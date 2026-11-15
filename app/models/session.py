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
    
    def touch(self, min_interval: timedelta = timedelta(minutes=5)) -> bool:
        """
        Aggiorna last_activity solo se è più vecchio di min_interval.
        Evita una scrittura sul DB a ogni richiesta del cliente.
        Ritorna True se il valore è cambiato (serve un commit).
        """
        now = datetime.utcnow()
        if self.last_activity is None or now - self.last_activity >= min_interval:
            self.last_activity = now
            return True
        return False

    @property
    def remaining_minutes(self):
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds() / 60)