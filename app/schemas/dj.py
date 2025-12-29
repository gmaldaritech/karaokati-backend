from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class DJRegister(BaseModel):
    full_name: str
    stage_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str

class DJLogin(BaseModel):
    email: EmailStr
    password: str

class DJResponse(BaseModel):
    id: int
    full_name: str
    stage_name: str
    email: str
    phone: Optional[str]
    qr_code_id: str
    email_verified: bool  # 🆕
    max_bookings_per_user: int
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    dj: DJResponse

class DJUpdate(BaseModel):
    """Schema per aggiornamento dati DJ"""
    full_name: Optional[str] = None
    stage_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    max_bookings_per_user: Optional[int] = Field(None, ge=1, le=999)

class PasswordChange(BaseModel):
    """Schema per cambio password"""
    current_password: str
    new_password: str = Field(min_length=8, description="Minimo 8 caratteri")

class PasswordResetRequest(BaseModel):
    """Schema per richiesta reset password"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema per reset password"""
    token: str
    new_password: str = Field(min_length=8, description="Minimo 8 caratteri")