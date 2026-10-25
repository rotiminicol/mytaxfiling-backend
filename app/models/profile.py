from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class ProfileBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    account_type: Optional[str] = None
    business_name: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None
    tin: Optional[str] = None
    nin: Optional[str] = None
    onboarded: Optional[bool] = None
    add_ons: Optional[List[str]] = None


class ProfileCreate(ProfileBase):
    id: str


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
