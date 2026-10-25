from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_user_id
from app.core.supabase_client import supabase_admin
from app.models.document import (
    ComplianceDocument, ComplianceDocumentCreate, ComplianceDocumentUpdate,
    DocumentReminder, DocumentReminderCreate, DocumentReminderUpdate
)

router = APIRouter()


# Compliance Documents Endpoints

@router.get("/compliance", response_model=List[ComplianceDocument])
async def get_compliance_documents(user_id: str = Depends(get_user_id)):
    """
    Get all compliance documents for the current user.
    """
    response = supabase_admin.table("compliance_documents").select("*").eq("user_id", user_id).order("expiry_date", asc=True).execute()
    return [ComplianceDocument(**doc) for doc in response.data]


@router.post("/compliance", response_model=ComplianceDocument)
async def create_compliance_document(
    document: ComplianceDocumentCreate,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new compliance document.
    """
    document_data = document.model_dump()
    document_data["user_id"] = user_id
    
    response = supabase_admin.table("compliance_documents").insert(document_data).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create document"
        )
    
    return ComplianceDocument(**response.data[0])


@router.get("/compliance/{document_id}", response_model=ComplianceDocument)
async def get_compliance_document(document_id: str, user_id: str = Depends(get_user_id)):
    """
    Get a specific compliance document.
    """
    response = supabase_admin.table("compliance_documents").select("*").eq("id", document_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return ComplianceDocument(**response.data[0])


@router.put("/compliance/{document_id}", response_model=ComplianceDocument)
async def update_compliance_document(
    document_id: str,
    document_update: ComplianceDocumentUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update a compliance document.
    """
    update_data = document_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("compliance_documents").update(update_data).eq("id", document_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return ComplianceDocument(**response.data[0])


@router.delete("/compliance/{document_id}")
async def delete_compliance_document(document_id: str, user_id: str = Depends(get_user_id)):
    """
    Delete a compliance document.
    """
    response = supabase_admin.table("compliance_documents").delete().eq("id", document_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {"message": "Document deleted successfully"}


@router.patch("/compliance/{document_id}/renewal")
async def submit_renewal(document_id: str, user_id: str = Depends(get_user_id)):
    """
    Submit a renewal application for a document.
    """
    response = supabase_admin.table("compliance_documents").update({"renewal_status": "pending"}).eq("id", document_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {"message": "Renewal submitted successfully", "document": ComplianceDocument(**response.data[0])}


# Document Reminders Endpoints

@router.get("/reminders", response_model=DocumentReminder)
async def get_document_reminders(user_id: str = Depends(get_user_id)):
    """
    Get document reminder preferences for the current user.
    """
    response = supabase_admin.table("document_reminders").select("*").eq("user_id", user_id).maybe_single().execute()
    
    if not response.data:
        # Create default reminders if not exist
        default_reminders = DocumentReminderCreate()
        reminder_data = default_reminders.model_dump()
        reminder_data["user_id"] = user_id
        response = supabase_admin.table("document_reminders").insert(reminder_data).execute()
        return DocumentReminder(**response.data[0])
    
    return DocumentReminder(**response.data)


@router.put("/reminders", response_model=DocumentReminder)
async def update_document_reminders(
    reminder_update: DocumentReminderUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update document reminder preferences.
    """
    update_data = reminder_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("document_reminders").update(update_data).eq("user_id", user_id).execute()
    
    if not response.data:
        # Create if not exists
        reminder_data = reminder_update.model_dump()
        reminder_data["user_id"] = user_id
        response = supabase_admin.table("document_reminders").insert(reminder_data).execute()
    
    return DocumentReminder(**response.data[0])
