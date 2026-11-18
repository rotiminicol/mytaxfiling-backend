import resend
from app.core.config import settings

# Initialize Resend client
resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """Service for sending emails using Resend"""

    @staticmethod
    async def send_email(
        to: str,
        subject: str,
        html_content: str,
        from_email: str = "MyTaxFiling <noreply@mytaxfiling.com.ng>",
    ):
        """
        Send an email using Resend

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email address (default: noreply@taxfiling.com.ng)

        Returns:
            Resend response object
        """
        try:
            params = {
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": html_content,
            }

            response = resend.Emails.send(params)
            return response
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

    @staticmethod
    async def send_otp_email(
        to: str,
        otp: str,
        from_email: str = "MyTaxFiling <noreply@mytaxfiling.com.ng>",
    ):
        """
        Send OTP email for verification

        Args:
            to: Recipient email address
            otp: One-time password
            from_email: Sender email address

        Returns:
            Resend response object
        """
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #18623f;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .otp {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #18623f;
                    text-align: center;
                    padding: 20px;
                    background-color: #e8f5e9;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MyTaxFiling</h1>
                </div>
                <div class="content">
                    <h2>Your Verification Code</h2>
                    <p>Use the following One-Time Password (OTP) to verify your account:</p>
                    <div class="otp">{otp}</div>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 MyTaxFiling. All rights reserved.</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await EmailService.send_email(
            to=to,
            subject="Your Verification Code - MyTaxFiling",
            html_content=html_content,
            from_email=from_email,
        )

    @staticmethod
    async def send_password_reset_otp_email(
        to: str,
        otp: str,
        from_email: str = "MyTaxFiling <noreply@mytaxfiling.com.ng>",
    ):
        html_content = f"""
        <html><body style="font-family:Arial,sans-serif;color:#333;line-height:1.6">
          <div style="max-width:600px;margin:auto;padding:24px">
            <div style="background:#18623f;color:#fff;padding:20px;text-align:center;border-radius:8px 8px 0 0"><h1>MyTaxFiling</h1></div>
            <div style="background:#f9f9f9;padding:30px;border-radius:0 0 8px 8px">
              <h2>Password reset code</h2><p>Use this one-time code to create a new password:</p>
              <div style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#18623f;text-align:center;padding:20px;background:#e8f5e9;border-radius:8px;margin:20px 0">{otp}</div>
              <p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes. If you did not request it, you can ignore this email.</p>
            </div>
          </div>
        </body></html>
        """
        return await EmailService.send_email(to=to, subject="Your Password Reset Code - MyTaxFiling", html_content=html_content, from_email=from_email)

    @staticmethod
    async def send_password_changed_email(
        to: str,
        from_email: str = "MyTaxFiling <noreply@mytaxfiling.com.ng>",
    ):
        html_content = """
        <html><body style="font-family:Arial,sans-serif;color:#333;line-height:1.6">
          <div style="max-width:600px;margin:auto;padding:24px">
            <div style="background:#18623f;color:#fff;padding:20px;text-align:center;border-radius:8px 8px 0 0"><h1>MyTaxFiling</h1></div>
            <div style="background:#f9f9f9;padding:30px;border-radius:0 0 8px 8px"><h2>Password changed</h2>
              <p>Your MyTaxFiling password was changed successfully. If you did not make this change, contact support immediately.</p>
            </div>
          </div>
        </body></html>
        """
        return await EmailService.send_email(to=to, subject="Your MyTaxFiling Password Was Changed", html_content=html_content, from_email=from_email)

    @staticmethod
    async def send_welcome_email(
        to: str,
        name: str,
        from_email: str = "MyTaxFiling <noreply@mytaxfiling.com.ng>",
    ):
        """
        Send welcome email to new users

        Args:
            to: Recipient email address
            name: User's name
            from_email: Sender email address

        Returns:
            Resend response object
        """
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #18623f;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #18623f;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MyTaxFiling</h1>
                </div>
                <div class="content">
                    <h2>Welcome to MyTaxFiling, {name}!</h2>
                    <p>Thank you for signing up for MyTaxFiling. We're excited to help you with your tax compliance needs.</p>
                    <p>With MyTaxFiling, you can:</p>
                    <ul>
                        <li>Claim rent relief up to ₦500,000</li>
                        <li>Issue NRS-compliant e-invoices</li>
                        <li>Manage your tax filings efficiently</li>
                        <li>Store all your important documents securely</li>
                    </ul>
                    <a href="http://localhost:5173" class="button">Get Started</a>
                    <p>If you have any questions, feel free to contact our support team.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 MyTaxFiling. All rights reserved.</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await EmailService.send_email(
            to=to,
            subject="Welcome to MyTaxFiling!",
            html_content=html_content,
            from_email=from_email,
        )

    @staticmethod
    async def send_password_reset_email(
        to: str,
        reset_link: str,
        from_email: str = "MyTaxFiling <noreply@mytaxfiling.com.ng>",
    ):
        """
        Send password reset email

        Args:
            to: Recipient email address
            reset_link: Password reset link
            from_email: Sender email address

        Returns:
            Resend response object
        """
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #18623f;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #18623f;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MyTaxFiling</h1>
                </div>
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your password for your MyTaxFiling account.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_link}" class="button">Reset Password</a>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this password reset, please ignore this email and your password will remain unchanged.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 MyTaxFiling. All rights reserved.</p>
                    <p>This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await EmailService.send_email(
            to=to,
            subject="Reset Your Password - MyTaxFiling",
            html_content=html_content,
            from_email=from_email,
        )


# Export email service instance
email_service = EmailService()
