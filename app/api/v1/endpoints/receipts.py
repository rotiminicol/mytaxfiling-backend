from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_user_id
from app.core.supabase_client import supabase_admin
from app.models.receipt import Receipt, ReceiptCreate, ReceiptUpdate

router = APIRouter()


@router.get("", response_model=List[Receipt])
async def get_receipts(user_id: str = Depends(get_user_id)):
    """
    Get all receipts for the current user.
    """
    response = supabase_admin.table("receipts").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return [Receipt(**receipt) for receipt in response.data]


@router.post("", response_model=Receipt)
async def create_receipt(
    receipt: ReceiptCreate,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new rent receipt.
    """
    receipt_data = receipt.model_dump()
    receipt_data["user_id"] = user_id
    
    response = supabase_admin.table("receipts").insert(receipt_data).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create receipt"
        )
    
    return Receipt(**response.data[0])


@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: str, user_id: str = Depends(get_user_id)):
    """
    Get a specific receipt.
    """
    response = supabase_admin.table("receipts").select("*").eq("id", receipt_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return Receipt(**response.data[0])


@router.put("/{receipt_id}", response_model=Receipt)
async def update_receipt(
    receipt_id: str,
    receipt_update: ReceiptUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update a receipt.
    """
    update_data = receipt_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("receipts").update(update_data).eq("id", receipt_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return Receipt(**response.data[0])


@router.delete("/{receipt_id}")
async def delete_receipt(receipt_id: str, user_id: str = Depends(get_user_id)):
    """
    Delete a receipt.
    """
    response = supabase_admin.table("receipts").delete().eq("id", receipt_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return {"message": "Receipt deleted successfully"}


@router.patch("/{receipt_id}/certify")
async def certify_receipt(receipt_id: str, user_id: str = Depends(get_user_id)):
    """
    Certify a receipt as official.
    """
    from datetime import datetime
    
    response = supabase_admin.table("receipts").update({
        "status": "certified",
        "certified_date": datetime.utcnow().isoformat()
    }).eq("id", receipt_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return {"message": "Receipt certified successfully", "receipt": Receipt(**response.data[0])}
