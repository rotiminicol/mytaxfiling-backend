from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.core.security import get_user_id
from app.core.rbac import require_admin
from app.core.supabase_client import supabase_admin
from app.models.profile import Profile
from app.models.subscription import UserRole, AdminAuditLog, AdminAuditLogCreate
from datetime import datetime

router = APIRouter()


@router.get("/users", response_model=List[Profile])
async def get_all_users(payload: Dict[str, Any] = Depends(require_admin)):
    """
    Get all users (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("profiles").select("*").order("created_at", desc=True).execute()
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "view_all_users",
        "details": {"count": len(response.data)}
    }).execute()
    
    return [Profile(**user) for user in response.data]


@router.get("/users/{user_id}", response_model=Profile)
async def get_user_by_id(user_id: str, payload: Dict[str, Any] = Depends(require_admin)):
    """
    Get a specific user by ID (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("profiles").select("*").eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "view_user",
        "target_user_id": user_id,
        "details": {}
    }).execute()
    
    return Profile(**response.data[0])


@router.put("/users/{user_id}/role", response_model=UserRole)
async def update_user_role(
    user_id: str,
    role: str,
    payload: Dict[str, Any] = Depends(require_admin)
):
    """
    Update a user's role (admin only).
    """
    admin_id = payload.get("sub")
    
    # Validate role
    valid_roles = ["admin", "moderator", "user"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if role already exists
    existing = supabase_admin.table("user_roles").select("*").eq("user_id", user_id).eq("role", role).execute()
    
    if existing.data:
        return UserRole(**existing.data[0])
    
    # Create new role
    response = supabase_admin.table("user_roles").insert({
        "user_id": user_id,
        "role": role
    }).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user role"
        )
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "update_user_role",
        "target_user_id": user_id,
        "details": {"new_role": role}
    }).execute()
    
    return UserRole(**response.data[0])


@router.delete("/users/{user_id}/role/{role}")
async def remove_user_role(
    user_id: str,
    role: str,
    payload: Dict[str, Any] = Depends(require_admin)
):
    """
    Remove a role from a user (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("user_roles").delete().eq("user_id", user_id).eq("role", role).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "remove_user_role",
        "target_user_id": user_id,
        "details": {"removed_role": role}
    }).execute()
    
    return {"message": "Role removed successfully"}


@router.get("/audit-log", response_model=List[AdminAuditLog])
async def get_audit_log(
    limit: int = 100,
    offset: int = 0,
    payload: Dict[str, Any] = Depends(require_admin)
):
    """
    Get admin audit log (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("admin_audit_log").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    
    return [AdminAuditLog(**log) for log in response.data]


@router.get("/audit-log/user/{user_id}", response_model=List[AdminAuditLog])
async def get_user_audit_log(
    user_id: str,
    limit: int = 100,
    payload: Dict[str, Any] = Depends(require_admin)
):
    """
    Get audit log for a specific user (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("admin_audit_log").select("*").eq("target_user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    
    return [AdminAuditLog(**log) for log in response.data]


@router.get("/documents/all", response_model=List[Dict[str, Any]])
async def get_all_documents(payload: Dict[str, Any] = Depends(require_admin)):
    """
    Get all compliance documents across all users (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("compliance_documents").select("*").order("created_at", desc=True).execute()
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "view_all_documents",
        "details": {"count": len(response.data)}
    }).execute()
    
    return response.data


@router.get("/invoices/all", response_model=List[Dict[str, Any]])
async def get_all_invoices(payload: Dict[str, Any] = Depends(require_admin)):
    """
    Get all invoices across all users (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("invoices").select("*").order("created_at", desc=True).execute()
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "view_all_invoices",
        "details": {"count": len(response.data)}
    }).execute()
    
    return response.data


@router.get("/receipts/all", response_model=List[Dict[str, Any]])
async def get_all_receipts(payload: Dict[str, Any] = Depends(require_admin)):
    """
    Get all receipts across all users (admin only).
    """
    admin_id = payload.get("sub")
    
    response = supabase_admin.table("receipts").select("*").order("created_at", desc=True).execute()
    
    # Log admin action
    supabase_admin.table("admin_audit_log").insert({
        "admin_id": admin_id,
        "action": "view_all_receipts",
        "details": {"count": len(response.data)}
    }).execute()
    
    return response.data
