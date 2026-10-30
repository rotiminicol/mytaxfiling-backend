from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.email_service import email_service

router = APIRouter()


class TestEmailRequest(BaseModel):
    email: str
    test_type: str = "otp"  # otp, welcome, or reset


@router.post("/test-email")
async def test_email(request: TestEmailRequest):
    """
    Test endpoint to verify Resend email service is working
    """
    try:
        if request.test_type == "otp":
            # Test OTP email
            from app.services.otp_service import otp_service
            otp = otp_service.generate_otp()
            response = await email_service.send_otp_email(
                to=request.email,
                otp=otp
            )
            return {
                "success": True,
                "message": "OTP test email sent successfully",
                "otp": otp,
                "response": response
            }

        elif request.test_type == "welcome":
            # Test welcome email
            response = await email_service.send_welcome_email(
                to=request.email,
                name="Test User"
            )
            return {
                "success": True,
                "message": "Welcome test email sent successfully",
                "response": response
            }

        elif request.test_type == "reset":
            # Test password reset email
            response = await email_service.send_password_reset_email(
                to=request.email,
                reset_link="http://localhost:5173/reset-password/test-token"
            )
            return {
                "success": True,
                "message": "Password reset test email sent successfully",
                "response": response
            }

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid test_type. Use 'otp', 'welcome', or 'reset'"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test email: {str(e)}"
        )
