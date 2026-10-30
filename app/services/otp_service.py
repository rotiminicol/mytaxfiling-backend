import random
import string
from datetime import datetime, timedelta
from typing import Optional
from app.services.email_service import email_service


class OTPService:
    """Service for generating and managing OTPs"""

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generate a random OTP

        Args:
            length: Length of the OTP (default: 6)

        Returns:
            Generated OTP string
        """
        digits = string.digits
        otp = "".join(random.choice(digits) for _ in range(length))
        return otp

    @staticmethod
    def calculate_expiry(minutes: int = 10) -> datetime:
        """
        Calculate OTP expiry time

        Args:
            minutes: Minutes until expiry (default: 10)

        Returns:
            Expiry datetime
        """
        return datetime.utcnow() + timedelta(minutes=minutes)

    @staticmethod
    def is_otp_valid(expiry: datetime) -> bool:
        """
        Check if OTP is still valid

        Args:
            expiry: Expiry datetime

        Returns:
            True if valid, False otherwise
        """
        return datetime.utcnow() < expiry

    @staticmethod
    async def send_otp_via_email(email: str, otp: str) -> dict:
        """
        Send OTP via email using Resend

        Args:
            email: Recipient email address
            otp: OTP to send

        Returns:
            Response from email service
        """
        try:
            response = await email_service.send_otp_email(to=email, otp=otp)
            return {"success": True, "message": "OTP sent successfully", "data": response}
        except Exception as e:
            return {"success": False, "message": f"Failed to send OTP: {str(e)}"}


# Export OTP service instance
otp_service = OTPService()
