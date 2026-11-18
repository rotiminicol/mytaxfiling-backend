from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class SignUpRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    plan: str = "free"
    account_type: Optional[str] = None
    add_ons: list[str] = Field(default_factory=list)

    @field_validator("full_name", "phone", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendOtpRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ProfilePatchRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tin: Optional[str] = None
    nin: Optional[str] = None
    organization: Optional[str] = None
    account_type: Optional[str] = None
    state_of_residence: Optional[str] = None
    employment_status: Optional[str] = None
    avatar_url: Optional[str] = None


class OnboardingPatchRequest(BaseModel):
    step: Optional[str] = None
    account_type: Optional[str] = None
    plan: Optional[str] = None
    billing_cycle: Optional[str] = None
    tin: Optional[str] = None
    organization: Optional[str] = None
    nin: Optional[str] = None
    state_of_residence: Optional[str] = None
    employment_status: Optional[str] = None
    onboarded: Optional[bool] = None


class SubscriptionPatchRequest(BaseModel):
    plan: str
    billing_cycle: Optional[str] = None


class AuthUserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    email_verified: bool
    onboarded: bool = False
    onboarding_step: Optional[str] = None
    state_of_residence: Optional[str] = None
    employment_status: Optional[str] = None
    tin: Optional[str] = None
    nin: Optional[str] = None
    organization: Optional[str] = None
    account_type: Optional[str] = None
    role: str = "user"
    created_at: datetime
    plan: str = "free"
    plan_billing_cycle: Optional[str] = None
    plan_start_date: Optional[datetime] = None
    plan_expires_at: Optional[datetime] = None
    add_ons: list[str] = Field(default_factory=list)


class AuthResponse(BaseModel):
    user: AuthUserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    success: bool = True
    message: str
    cooldown_seconds: int = 0
