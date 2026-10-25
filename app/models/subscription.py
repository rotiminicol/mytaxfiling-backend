from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionBase(BaseModel):
    plan: str
    status: str
    billing_cycle: Optional[str] = None
    provider: Optional[str] = None
    provider_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    status: Optional[str] = None
    billing_cycle: Optional[str] = None
    provider: Optional[str] = None
    provider_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at: Optional[datetime] = None


class Subscription(SubscriptionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleBase(BaseModel):
    role: str  # "admin" | "moderator" | "user"


class UserRoleCreate(UserRoleBase):
    pass


class UserRole(UserRoleBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminAuditLogBase(BaseModel):
    action: str
    target_user_id: Optional[str] = None
    details: Optional[dict] = None


class AdminAuditLogCreate(AdminAuditLogBase):
    pass


class AdminAuditLog(AdminAuditLogBase):
    id: str
    admin_id: str
    created_at: datetime

    class Config:
        from_attributes = True
