from pydantic import BaseModel
from typing import Optional

class VenueCreate(BaseModel):
    name: str
    address: Optional[str] = None
    capacity: Optional[int] = None
    notes: Optional[str] = None

class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    notes: Optional[str] = None

class VenueResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    capacity: Optional[int]
    notes: Optional[str] = None
    active: bool
    
    class Config:
        from_attributes = True