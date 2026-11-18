from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Optional
import os


class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = ""
    SUPABASE_SECRET_KEY: Optional[str] = ""
    SUPABASE_JWKS_URL: Optional[str] = ""

    # Database Configuration
    DATABASE_URL: Optional[str] = ""

    # JWT Configuration
    JWT_SECRET: str = "default-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 60
    REFRESH_TOKEN_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 15
    OTP_RESEND_COOLDOWN_SECONDS: int = 30
    OTP_MAX_ATTEMPTS: int = 5
    PASSWORD_RESET_URL: str = "http://localhost:5173/customer-dashboard/reset-password"

    # Email Configuration (Resend)
    RESEND_API_KEY: Optional[str] = ""

    # CORS Configuration
    FRONTEND_URLS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://taxfiling.com.ng",
        "https://www.taxfiling.com.ng"
    ]

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "MyTaxFiling API"

    @field_validator("FRONTEND_URLS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [url.strip() for url in v.split(",") if url.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
