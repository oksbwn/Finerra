from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from backend.app.modules.auth.models import UserRole

class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class TenantRead(TenantBase):
    id: UUID
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.ADULT

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    tenant_id: UUID
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: Optional[str] = None
    tenant_id: Optional[str] = None
