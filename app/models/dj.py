from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class DJ(Base):
    __tablename__ = "djs"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    stage_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    qr_code_id = Column(String(50), unique=True, nullable=False, index=True)
    max_bookings_per_user = Column(Integer, default=999, nullable=False)

    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships (le aggiungeremo dopo)
    venues = relationship("Venue", back_populates="dj", cascade="all, delete-orphan")
    songs = relationship("Song", back_populates="dj", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="dj", cascade="all, delete-orphan")