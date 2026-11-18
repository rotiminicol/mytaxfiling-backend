from datetime import datetime, timedelta, timezone
import logging
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.auth_crypto import (
    create_access_token,
    create_refresh_token,
    generate_otp,
    hash_otp,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.core.security import get_user_id
from app.core.supabase_client import supabase_admin
from app.models.auth import (
    AuthResponse,
    AuthUserResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ResendOtpRequest,
    ResetPasswordRequest,
    SignUpRequest,
    VerifyOtpRequest,
    OnboardingPatchRequest,
    ProfilePatchRequest,
    SubscriptionPatchRequest,
)
from app.services.email_service import email_service

router = APIRouter()
logger = logging.getLogger(__name__)


def _db():
    if supabase_admin is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return supabase_admin


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_phone(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if digits.startswith("234"):
        return "+" + digits
    if digits.startswith("0"):
        return "+234" + digits[1:]
    return "+234" + digits


def _row(response: Any) -> dict | None:
    data = getattr(response, "data", None)
    if isinstance(data, list):
        return data[0] if data else None
    return data if isinstance(data, dict) else None


async def _send_otp(email: str, purpose: str, full_name: str | None = None) -> int:
    db = _db()
    latest = (
        db.table("auth_otp_codes")
        .select("created_at,last_sent_at")
        .eq("email", email)
        .eq("purpose", purpose)
        .is_("consumed_at", "null")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    latest_row = _row(latest)
    if latest_row and latest_row.get("last_sent_at"):
        sent_at = datetime.fromisoformat(str(latest_row["last_sent_at"]).replace("Z", "+00:00"))
        elapsed = (_now() - sent_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Please wait before requesting another code.",
                    "cooldown_seconds": max(1, int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)),
                },
            )

    code = generate_otp()
    now = _now()
    expires = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    db.table("auth_otp_codes").update({"consumed_at": now.isoformat()}).eq("email", email).eq("purpose", purpose).is_("consumed_at", "null").execute()
    db.table("auth_otp_codes").insert({
        "email": email,
        "purpose": purpose,
        "code_hash": hash_otp(code),
        "expires_at": expires.isoformat(),
        "last_sent_at": now.isoformat(),
    }).execute()

    try:
        if purpose == "signup_verification":
            await email_service.send_otp_email(to=email, otp=code)
        else:
            await email_service.send_password_reset_otp_email(to=email, otp=code)
    except Exception:
        logger.exception("OTP email delivery failed for purpose=%s", purpose)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Verification email could not be sent. Check the Resend API key and verified sender domain.",
        )
    return settings.OTP_RESEND_COOLDOWN_SECONDS


def _verify_otp(email: str, code: str, purpose: str) -> None:
    db = _db()
    response = (
        db.table("auth_otp_codes")
        .select("*")
        .eq("email", email)
        .eq("purpose", purpose)
        .is_("consumed_at", "null")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    record = _row(response)
    if not record:
        raise HTTPException(status_code=400, detail="No active code found. Request a new OTP.")
    expires = datetime.fromisoformat(str(record["expires_at"]).replace("Z", "+00:00"))
    if expires <= _now():
        raise HTTPException(status_code=400, detail="This OTP has expired. Request a new code.")
    attempts = int(record.get("attempts") or 0)
    if attempts >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Too many incorrect attempts. Request a new code.")
    if not __import__("hmac").compare_digest(str(record["code_hash"]), hash_otp(code)):
        db.table("auth_otp_codes").update({"attempts": attempts + 1}).eq("id", record["id"]).execute()
        raise HTTPException(status_code=400, detail="Incorrect OTP. Check your email and try again.")
    db.table("auth_otp_codes").update({"consumed_at": _now().isoformat()}).eq("id", record["id"]).execute()


def _get_user(user_id: str) -> dict:
    db = _db()
    user = _row(db.table("app_users").select("*").eq("id", user_id).maybe_single().execute())
    if not user or user.get("status") != "active":
        raise HTTPException(status_code=401, detail="Account is unavailable")
    profile = _row(db.table("profiles").select("*").eq("id", user_id).maybe_single().execute()) or {}
    subscription = _row(db.table("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()) or {}
    roles = db.table("user_roles").select("role").eq("user_id", user_id).execute().data or []
    role = "admin" if any(r.get("role") == "admin" for r in roles) else "user"
    return {"user": user, "profile": profile, "subscription": subscription, "role": role}


def _user_response(context: dict) -> AuthUserResponse:
    user, profile, sub = context["user"], context["profile"], context["subscription"]
    return AuthUserResponse(
        id=user["id"], email=user["email"], full_name=profile.get("full_name") or "",
        phone=profile.get("phone") or user.get("phone"),
        email_verified=bool(user.get("email_verified_at")), onboarded=bool(profile.get("onboarded")),
        onboarding_step=profile.get("onboarding_step"), state_of_residence=profile.get("state_of_residence"),
        employment_status=profile.get("employment_status"), tin=profile.get("tin"), nin=profile.get("nin"),
        organization=profile.get("organization") or profile.get("business_name"), account_type=profile.get("account_type"),
        role=context["role"], created_at=user["created_at"], plan=sub.get("plan", "free"),
        plan_billing_cycle=sub.get("billing_cycle"), plan_start_date=sub.get("current_period_start") or sub.get("created_at"),
        plan_expires_at=sub.get("current_period_end"), add_ons=profile.get("add_ons") or [],
    )


def _auth_response(context: dict) -> AuthResponse:
    user = context["user"]
    role = context["role"]
    return AuthResponse(
        user=_user_response(context),
        access_token=create_access_token(user["id"], user["email"], role),
        refresh_token=create_refresh_token(user["id"], user["email"], role),
    )


@router.post("/signup", response_model=MessageResponse, status_code=202)
async def signup(request: SignUpRequest):
    db = _db()
    email = str(request.email).lower().strip()
    phone = _clean_phone(request.phone)
    existing = _row(db.table("app_users").select("id").eq("email", email).maybe_single().execute())
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists. Please log in.")
    existing_phone = _row(db.table("app_users").select("id").eq("phone", phone).maybe_single().execute())
    if existing_phone:
        raise HTTPException(status_code=409, detail="This phone number is already associated with another account.")
    pending = _row(db.table("auth_signup_requests").select("id").eq("email", email).maybe_single().execute())
    payload = {
        "email": email, "phone": phone, "full_name": request.full_name, "password_hash": hash_password(request.password),
        "desired_plan": request.plan if request.plan in {"free", "deluxe", "premium"} else "free",
        "account_type": request.account_type, "add_ons": request.add_ons,
        "expires_at": (_now() + timedelta(minutes=30)).isoformat(), "updated_at": _now().isoformat(),
    }
    if pending:
        db.table("auth_signup_requests").update(payload).eq("id", pending["id"]).execute()
    else:
        db.table("auth_signup_requests").insert(payload).execute()
    cooldown = await _send_otp(email, "signup_verification", request.full_name)
    return MessageResponse(message="Verification code sent. Enter the OTP to finish creating your account.", cooldown_seconds=cooldown)


@router.post("/signup/verify", response_model=AuthResponse)
async def verify_signup(request: VerifyOtpRequest):
    db = _db()
    email = str(request.email).lower().strip()
    _verify_otp(email, request.code, "signup_verification")
    pending = _row(db.table("auth_signup_requests").select("*").eq("email", email).maybe_single().execute())
    if not pending or datetime.fromisoformat(str(pending["expires_at"]).replace("Z", "+00:00")) <= _now():
        raise HTTPException(status_code=400, detail="Signup session expired. Please start again.")
    user_id = str(uuid4())
    now = _now().isoformat()
    db.table("app_users").insert({
        "id": user_id, "email": email, "phone": pending.get("phone"), "password_hash": pending["password_hash"],
        "email_verified_at": now, "created_at": now, "updated_at": now,
    }).execute()
    db.table("profiles").insert({
        "id": user_id, "email": email, "full_name": pending["full_name"], "phone": pending.get("phone"),
        "account_type": pending.get("account_type"), "add_ons": pending.get("add_ons") or [],
        "onboarded": False, "onboarding_step": "plan" if pending.get("account_type") else "account",
    }).execute()
    db.table("subscriptions").insert({"user_id": user_id, "plan": pending.get("desired_plan", "free"), "status": "active"}).execute()
    db.table("user_roles").insert({"user_id": user_id, "role": "user"}).execute()
    db.table("auth_signup_requests").delete().eq("id", pending["id"]).execute()
    try:
        await email_service.send_welcome_email(to=email, name=pending["full_name"])
    except Exception:
        pass
    return _auth_response(_get_user(user_id))


@router.post("/signup/resend", response_model=MessageResponse)
async def resend_signup(request: ResendOtpRequest):
    email = str(request.email).lower().strip()
    pending = _row(_db().table("auth_signup_requests").select("full_name").eq("email", email).maybe_single().execute())
    if not pending:
        raise HTTPException(status_code=404, detail="No pending signup found for this email.")
    cooldown = await _send_otp(email, "signup_verification", pending.get("full_name"))
    return MessageResponse(message="A new verification code has been sent.", cooldown_seconds=cooldown)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    db = _db()
    identifier = request.identifier.strip()
    email = identifier.lower() if "@" in identifier else None
    if not email:
        phone = _clean_phone(identifier)
        found = _row(db.table("app_users").select("email").eq("phone", phone).maybe_single().execute())
        email = found.get("email") if found else None
    user = _row(db.table("app_users").select("*").eq("email", email).maybe_single().execute()) if email else None
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Incorrect email/phone or password.")
    if not user.get("email_verified_at"):
        raise HTTPException(status_code=403, detail={"message": "Please verify your email first.", "email_verified": False, "email": user["email"]})
    db.table("app_users").update({"last_login_at": _now().isoformat(), "updated_at": _now().isoformat()}).eq("id", user["id"]).execute()
    return _auth_response(_get_user(user["id"]))


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(request: ResendOtpRequest):
    return await resend_signup(request)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    email = str(request.email).lower().strip()
    user = _row(_db().table("app_users").select("id").eq("email", email).maybe_single().execute())
    # Do not disclose whether the address exists. Existing users receive the code.
    if user:
        await _send_otp(email, "password_reset")
    return MessageResponse(message="If an account exists for this email, a reset code has been sent.")


@router.post("/forgot-password/resend", response_model=MessageResponse)
async def resend_password_reset(request: ResendOtpRequest):
    return await forgot_password(request)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    email = str(request.email).lower().strip()
    _verify_otp(email, request.code, "password_reset")
    db = _db()
    user = _row(db.table("app_users").select("id").eq("email", email).maybe_single().execute())
    if not user:
        raise HTTPException(status_code=400, detail="Unable to reset this account.")
    db.table("app_users").update({"password_hash": hash_password(request.new_password), "updated_at": _now().isoformat()}).eq("id", user["id"]).execute()
    try:
        await email_service.send_password_changed_email(email)
    except Exception:
        pass
    return MessageResponse(message="Password updated successfully. You can now log in.")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(request: ChangePasswordRequest, user_id: str = Depends(get_user_id)):
    db = _db()
    user = _row(db.table("app_users").select("*").eq("id", user_id).maybe_single().execute())
    if not user or not verify_password(request.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    db.table("app_users").update({"password_hash": hash_password(request.new_password), "updated_at": _now().isoformat()}).eq("id", user_id).execute()
    return MessageResponse(message="Password changed successfully.")


@router.get("/me", response_model=AuthUserResponse)
async def current_user(user_id: str = Depends(get_user_id)):
    return _user_response(_get_user(user_id))


@router.post("/logout", response_model=MessageResponse)
async def logout(user_id: str = Depends(get_user_id)):
    return MessageResponse(message="Signed out successfully.")


@router.patch("/me", response_model=AuthUserResponse)
async def update_me(request: ProfilePatchRequest, user_id: str = Depends(get_user_id)):
    db = _db()
    patch = request.model_dump(exclude_unset=True)
    if "full_name" in patch:
        patch["full_name"] = patch["full_name"].strip() if patch["full_name"] else patch["full_name"]
    if "email" in patch and patch["email"]:
        patch["email"] = str(patch["email"]).lower()
    if "phone" in patch and patch["phone"]:
        patch["phone"] = _clean_phone(patch["phone"])
    profile_patch = {k: v for k, v in patch.items() if k not in {"email", "phone"}}
    if "organization" in profile_patch:
        profile_patch["business_name"] = profile_patch["organization"]
    if profile_patch:
        db.table("profiles").update(profile_patch).eq("id", user_id).execute()
    user_patch = {k: patch[k] for k in ("email", "phone") if k in patch}
    if user_patch:
        db.table("app_users").update(user_patch | {"updated_at": _now().isoformat()}).eq("id", user_id).execute()
    return _user_response(_get_user(user_id))


@router.patch("/me/onboarding", response_model=AuthUserResponse)
async def update_onboarding(request: OnboardingPatchRequest, user_id: str = Depends(get_user_id)):
    db = _db()
    data = request.model_dump(exclude_unset=True)
    profile_patch = {
        "onboarding_step": data.pop("step", None),
        "account_type": data.pop("account_type", None),
        "tin": data.pop("tin", None),
        "organization": data.pop("organization", None),
        "nin": data.pop("nin", None),
        "state_of_residence": data.pop("state_of_residence", None),
        "employment_status": data.pop("employment_status", None),
        "onboarded": data.pop("onboarded", None),
    }
    profile_patch = {k: v for k, v in profile_patch.items() if v is not None}
    if "organization" in profile_patch:
        profile_patch["business_name"] = profile_patch["organization"]
    if profile_patch:
        db.table("profiles").update(profile_patch).eq("id", user_id).execute()
    if data.get("plan"):
        plan = data["plan"] if data["plan"] in {"free", "deluxe", "premium"} else "free"
        sub_patch = {"plan": plan, "status": "active", "updated_at": _now().isoformat()}
        if data.get("billing_cycle"):
            sub_patch["billing_cycle"] = data["billing_cycle"]
        db.table("subscriptions").update(sub_patch).eq("user_id", user_id).execute()
    return _user_response(_get_user(user_id))


@router.patch("/me/subscription", response_model=AuthUserResponse)
async def update_subscription(request: SubscriptionPatchRequest, user_id: str = Depends(get_user_id)):
    if request.plan not in {"free", "deluxe", "premium"}:
        raise HTTPException(status_code=400, detail="Unsupported subscription plan")
    db = _db()
    patch = {"plan": request.plan, "status": "active", "updated_at": _now().isoformat()}
    if request.billing_cycle:
        patch["billing_cycle"] = request.billing_cycle
    db.table("subscriptions").update(patch).eq("user_id", user_id).execute()
    return _user_response(_get_user(user_id))


@router.delete("/me", response_model=MessageResponse)
async def delete_me(user_id: str = Depends(get_user_id)):
    db = _db()
    for table, column in [
        ("document_reminders", "user_id"), ("compliance_documents", "user_id"),
        ("invoice_activities", "user_id"), ("invoices", "user_id"),
        ("invoice_templates", "user_id"), ("invoice_clients", "user_id"),
        ("receipts", "user_id"), ("feature_usage", "user_id"),
        ("payment_transactions", "user_id"), ("subscriptions", "user_id"),
        ("user_roles", "user_id"), ("profiles", "id"), ("app_users", "id"),
    ]:
        try:
            db.table(table).delete().eq(column, user_id).execute()
        except Exception:
            pass
    return MessageResponse(message="Account deleted successfully.")
