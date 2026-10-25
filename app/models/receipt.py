from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ReceiptBase(BaseModel):
    status: str = "draft"
    taxpayer: Dict[str, Any] = {}
    landlord: Dict[str, Any] = {}
    employer: Dict[str, Any] = {}
    declaration: bool = False
    signature_data: Optional[str] = None
    typed_signature: Optional[str] = None
    sig_mode: Optional[str] = None
    certified_date: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    status: Optional[str] = None
    taxpayer: Optional[Dict[str, Any]] = None
    landlord: Optional[Dict[str, Any]] = None
    employer: Optional[Dict[str, Any]] = None
    declaration: Optional[bool] = None
    signature_data: Optional[str] = None
    typed_signature: Optional[str] = None
    sig_mode: Optional[str] = None
    certified_date: Optional[str] = None


class Receipt(ReceiptBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
