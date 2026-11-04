from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class BookingCreate(BaseModel):
    user_name: str
    song: str
    key: Optional[str] = "0"
    notes: Optional[str] = None
    venue_id: int
    is_free_request: bool = False

class BookingResponse(BaseModel):
    id: int
    user_name: str
    song: str
    key: str
    notes: Optional[str] = None
    status: str
    venue_id: int
    session_id: Optional[uuid.UUID] = None  # ✅ NUOVO
    created_at: datetime
    is_free_request: bool = False
    
    class Config:
        from_attributes = True

class BookingWithVenue(BaseModel):
    id: int
    user_name: str
    song: str
    key: str
    notes: Optional[str] = None
    status: str
    venue_name: str
    session_id: Optional[uuid.UUID] = None  # ✅ NUOVO
    created_at: datetime
    is_free_request: bool = False