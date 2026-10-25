from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_user_id
from app.core.supabase_client import supabase_admin
from app.models.invoice import (
    InvoiceClient, InvoiceClientCreate, InvoiceClientUpdate,
    Invoice, InvoiceCreate, InvoiceUpdate,
    InvoiceTemplate, InvoiceTemplateCreate, InvoiceTemplateUpdate,
    InvoiceActivity, InvoiceActivityCreate
)

router = APIRouter()
clients_router = APIRouter()
templates_router = APIRouter()
activities_router = APIRouter()


# Invoice Clients Endpoints

@clients_router.get("", response_model=List[InvoiceClient])
async def get_invoice_clients(user_id: str = Depends(get_user_id)):
    """
    Get all invoice clients for the current user.
    """
    response = supabase_admin.table("invoice_clients").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return [InvoiceClient(**client) for client in response.data]


@router.post("/clients", response_model=InvoiceClient)
async def create_invoice_client(
    client: InvoiceClientCreate,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new invoice client.
    """
    client_data = client.model_dump()
    client_data["user_id"] = user_id
    
    response = supabase_admin.table("invoice_clients").insert(client_data).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create client"
        )
    
    return InvoiceClient(**response.data[0])


@clients_router.get("/{client_id}", response_model=InvoiceClient)
async def get_invoice_client(client_id: str, user_id: str = Depends(get_user_id)):
    """
    Get a specific invoice client.
    """
    response = supabase_admin.table("invoice_clients").select("*").eq("id", client_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return InvoiceClient(**response.data[0])


@clients_router.put("/{client_id}", response_model=InvoiceClient)
async def update_invoice_client(
    client_id: str,
    client_update: InvoiceClientUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update an invoice client.
    """
    update_data = client_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("invoice_clients").update(update_data).eq("id", client_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return InvoiceClient(**response.data[0])


@clients_router.delete("/{client_id}")
async def delete_invoice_client(client_id: str, user_id: str = Depends(get_user_id)):
    """
    Delete an invoice client.
    """
    response = supabase_admin.table("invoice_clients").delete().eq("id", client_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return {"message": "Client deleted successfully"}


# Invoices Endpoints

@router.get("", response_model=List[Invoice])
async def get_invoices(user_id: str = Depends(get_user_id)):
    """
    Get all invoices for the current user.
    """
    response = supabase_admin.table("invoices").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return [Invoice(**invoice) for invoice in response.data]


@router.post("", response_model=Invoice)
async def create_invoice(
    invoice: InvoiceCreate,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new invoice.
    """
    invoice_data = invoice.model_dump()
    invoice_data["user_id"] = user_id
    
    response = supabase_admin.table("invoices").insert(invoice_data).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create invoice"
        )
    
    # Log activity
    activity_data = {
        "user_id": user_id,
        "invoice_id": response.data[0]["id"],
        "client_id": invoice_data.get("client_id"),
        "type": "created",
        "title": "Draft created",
        "detail": f"Invoice {invoice.invoice_number} started"
    }
    supabase_admin.table("invoice_activities").insert(activity_data).execute()
    
    return Invoice(**response.data[0])


@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str, user_id: str = Depends(get_user_id)):
    """
    Get a specific invoice.
    """
    response = supabase_admin.table("invoices").select("*").eq("id", invoice_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return Invoice(**response.data[0])


@router.put("/{invoice_id}", response_model=Invoice)
async def update_invoice(
    invoice_id: str,
    invoice_update: InvoiceUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update an invoice.
    """
    update_data = invoice_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("invoices").update(update_data).eq("id", invoice_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return Invoice(**response.data[0])


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str, user_id: str = Depends(get_user_id)):
    """
    Delete an invoice.
    """
    response = supabase_admin.table("invoices").delete().eq("id", invoice_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return {"message": "Invoice deleted successfully"}


@router.patch("/{invoice_id}/send")
async def send_invoice(invoice_id: str, user_id: str = Depends(get_user_id)):
    """
    Mark an invoice as sent.
    """
    from datetime import datetime
    
    response = supabase_admin.table("invoices").update({
        "status": "sent",
        "sent_at": datetime.utcnow().isoformat()
    }).eq("id", invoice_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Log activity
    invoice = response.data[0]
    activity_data = {
        "user_id": user_id,
        "invoice_id": invoice_id,
        "client_id": invoice.get("client_id"),
        "type": "sent",
        "title": "Invoice sent",
        "detail": f"Sent {invoice['invoice_number']}"
    }
    supabase_admin.table("invoice_activities").insert(activity_data).execute()
    
    return {"message": "Invoice sent successfully", "invoice": Invoice(**invoice)}


@router.patch("/{invoice_id}/pay")
async def mark_invoice_paid(invoice_id: str, user_id: str = Depends(get_user_id)):
    """
    Mark an invoice as paid.
    """
    from datetime import datetime
    
    response = supabase_admin.table("invoices").update({
        "status": "paid",
        "paid_at": datetime.utcnow().isoformat()
    }).eq("id", invoice_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Log activity
    invoice = response.data[0]
    activity_data = {
        "user_id": user_id,
        "invoice_id": invoice_id,
        "client_id": invoice.get("client_id"),
        "type": "paid",
        "title": "Invoice paid",
        "detail": f"Payment received for {invoice['invoice_number']}"
    }
    supabase_admin.table("invoice_activities").insert(activity_data).execute()
    
    return {"message": "Invoice marked as paid", "invoice": Invoice(**invoice)}


# Invoice Templates Endpoints

@templates_router.get("", response_model=List[InvoiceTemplate])
async def get_invoice_templates(user_id: str = Depends(get_user_id)):
    """
    Get all invoice templates for the current user.
    """
    response = supabase_admin.table("invoice_templates").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return [InvoiceTemplate(**template) for template in response.data]


@router.post("/templates", response_model=InvoiceTemplate)
async def create_invoice_template(
    template: InvoiceTemplateCreate,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new invoice template.
    """
    template_data = template.model_dump()
    template_data["user_id"] = user_id
    
    response = supabase_admin.table("invoice_templates").insert(template_data).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create template"
        )
    
    return InvoiceTemplate(**response.data[0])


@templates_router.get("/{template_id}", response_model=InvoiceTemplate)
async def get_invoice_template(template_id: str, user_id: str = Depends(get_user_id)):
    """
    Get a specific invoice template.
    """
    response = supabase_admin.table("invoice_templates").select("*").eq("id", template_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return InvoiceTemplate(**response.data[0])


@templates_router.put("/{template_id}", response_model=InvoiceTemplate)
async def update_invoice_template(
    template_id: str,
    template_update: InvoiceTemplateUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update an invoice template.
    """
    update_data = template_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("invoice_templates").update(update_data).eq("id", template_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return InvoiceTemplate(**response.data[0])


@templates_router.delete("/{template_id}")
async def delete_invoice_template(template_id: str, user_id: str = Depends(get_user_id)):
    """
    Delete an invoice template.
    """
    response = supabase_admin.table("invoice_templates").delete().eq("id", template_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return {"message": "Template deleted successfully"}


@templates_router.patch("/{template_id}/use")
async def increment_template_usage(template_id: str, user_id: str = Depends(get_user_id)):
    """
    Increment the usage count of a template.
    """
    # Get current usage count
    response = supabase_admin.table("invoice_templates").select("usage_count").eq("id", template_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    current_count = response.data[0].get("usage_count", 0)
    
    response = supabase_admin.table("invoice_templates").update({
        "usage_count": current_count + 1
    }).eq("id", template_id).eq("user_id", user_id).execute()
    
    return {"message": "Template usage incremented", "template": InvoiceTemplate(**response.data[0])}


# Invoice Activities Endpoints

@activities_router.get("", response_model=List[InvoiceActivity])
async def get_invoice_activities(user_id: str = Depends(get_user_id)):
    """
    Get invoice activities for the current user.
    """
    response = supabase_admin.table("invoice_activities").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(50).execute()
    return [InvoiceActivity(**activity) for activity in response.data]
