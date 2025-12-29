from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class SessionCreate(BaseModel):
    """Schema per creare una nuova sessione"""
    qr_code_id: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class SessionResponse(BaseModel):
    """Schema per risposta sessione creata"""
    id: uuid.UUID
    dj_id: int
    expires_at: datetime
    remaining_minutes: int
    
    class Config:
        from_attributes = True

class SessionValidation(BaseModel):
    """Schema per validazione sessione"""
    valid: bool
    session_id: Optional[uuid.UUID] = None
    dj: Optional[dict] = None
    active_venue: Optional[dict] = None
    expires_at: Optional[datetime] = None
    remaining_minutes: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None