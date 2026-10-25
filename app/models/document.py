from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComplianceDocumentBase(BaseModel):
    type: str
    title: str
    reference: str
    issuer: Optional[str] = None
    expiry_date: str
    issue_date: Optional[str] = None
    notes: Optional[str] = None
    attachment_name: Optional[str] = None
    renewal_status: str = "none"


class ComplianceDocumentCreate(ComplianceDocumentBase):
    pass


class ComplianceDocumentUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    reference: Optional[str] = None
    issuer: Optional[str] = None
    expiry_date: Optional[str] = None
    issue_date: Optional[str] = None
    notes: Optional[str] = None
    attachment_name: Optional[str] = None
    renewal_status: Optional[str] = None


class ComplianceDocument(ComplianceDocumentBase):
    id: str
    user_id: str
    last_renewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentReminderBase(BaseModel):
    whatsapp: bool = True
    email_reports: bool = True
    auto_renew: bool = False
    phone: str = ""


class DocumentReminderCreate(DocumentReminderBase):
    pass


class DocumentReminderUpdate(DocumentReminderBase):
    pass


class DocumentReminder(DocumentReminderBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
