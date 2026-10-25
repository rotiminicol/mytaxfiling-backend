from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_user_id
from app.core.supabase_client import supabase_admin
from app.models.profile import Profile, ProfileCreate, ProfileUpdate

router = APIRouter()


@router.get("/me", response_model=Profile)
async def get_current_profile(user_id: str = Depends(get_user_id)):
    """
    Get current user's profile.
    """
    response = supabase_admin.table("profiles").select("*").eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return Profile(**response.data[0])


@router.put("/me", response_model=Profile)
async def update_current_profile(
    profile_update: ProfileUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    Update current user's profile.
    """
    # Filter out None values
    update_data = profile_update.model_dump(exclude_unset=True)
    
    response = supabase_admin.table("profiles").update(update_data).eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return Profile(**response.data[0])


@router.get("/{profile_id}", response_model=Profile)
async def get_profile(profile_id: str, user_id: str = Depends(get_user_id)):
    """
    Get a specific profile (admin only or own profile).
    """
    # Users can only access their own profile unless they're admin
    if profile_id != user_id:
        # Check if user is admin
        role_response = supabase_admin.table("user_roles").select("*").eq("user_id", user_id).eq("role", "admin").execute()
        if not role_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this profile"
            )
    
    response = supabase_admin.table("profiles").select("*").eq("id", profile_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return Profile(**response.data[0])
