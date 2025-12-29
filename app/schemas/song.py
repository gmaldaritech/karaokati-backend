from pydantic import BaseModel, Field
from typing import List

class SongCreate(BaseModel):
    file_name: str

class SongBulkCreate(BaseModel):
    songs: List[str]

class SongResponse(BaseModel):
    id: int
    file_name: str
    
    class Config:
        from_attributes = True

class SongListResponse(BaseModel):
    songs: List[SongResponse]
    total: int
    pages: int
    current_page: int