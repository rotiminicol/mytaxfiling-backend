from fastapi import HTTPException, status, Depends
from typing import Dict, Any
from app.core.security import verify_jwt_token
from app.core.supabase_client import supabase_admin


async def require_admin(payload: Dict[str, Any] = Depends(verify_jwt_token)) -> Dict[str, Any]:
    """
    Require admin role to access endpoint.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id",
        )
    
    # Check if user has admin role
    response = supabase_admin.table("user_roles").select("*").eq("user_id", user_id).eq("role", "admin").execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return payload


async def require_moderator_or_admin(payload: Dict[str, Any] = Depends(verify_jwt_token)) -> Dict[str, Any]:
    """
    Require moderator or admin role to access endpoint.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id",
        )
    
    # Check if user has moderator or admin role
    response = supabase_admin.table("user_roles").select("*").eq("user_id", user_id).in_("role", ["admin", "moderator"]).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin access required"
        )
    
    return payload
