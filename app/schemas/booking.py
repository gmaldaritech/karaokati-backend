from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class BookingCreate(BaseModel):
    user_name: str
    song: str
    key: Optional[str] = "0"
    venue_id: int

class BookingResponse(BaseModel):
    id: int
    user_name: str
    song: str
    key: str
    status: str
    venue_id: int
    session_id: Optional[uuid.UUID] = None  # ✅ NUOVO
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookingWithVenue(BaseModel):
    id: int
    user_name: str
    song: str
    key: str
    status: str
    venue_name: str
    session_id: Optional[uuid.UUID] = None  # ✅ NUOVO
    created_at: datetime