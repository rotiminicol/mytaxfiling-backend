from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InvoiceClientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None


class InvoiceClientCreate(InvoiceClientBase):
    pass


class InvoiceClientUpdate(InvoiceClientBase):
    pass


class InvoiceClient(InvoiceClientBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceLine(BaseModel):
    id: str
    description: str
    qty: int
    price: float


class InvoiceBase(BaseModel):
    client_id: Optional[str] = None
    invoice_number: str
    status: str = "draft"
    issue_date: str
    due_date: str
    notes: Optional[str] = None
    lines: List[dict] = []
    subtotal: float = 0
    vat: float = 0
    total: float = 0


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    client_id: Optional[str] = None
    invoice_number: Optional[str] = None
    status: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    lines: Optional[List[dict]] = None
    subtotal: Optional[float] = None
    vat: Optional[float] = None
    total: Optional[float] = None
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None


class Invoice(InvoiceBase):
    id: str
    user_id: str
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceTemplateBase(BaseModel):
    name: str
    description: str = ""
    lines: List[dict] = []
    usage_count: int = 0


class InvoiceTemplateCreate(InvoiceTemplateBase):
    pass


class InvoiceTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    lines: Optional[List[dict]] = None
    usage_count: Optional[int] = None


class InvoiceTemplate(InvoiceTemplateBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceActivityBase(BaseModel):
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None
    type: str
    title: str
    detail: str = ""


class InvoiceActivityCreate(InvoiceActivityBase):
    pass


class InvoiceActivity(InvoiceActivityBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
