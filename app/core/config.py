from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_ANON_KEY: str
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    # CORS Configuration
    FRONTEND_URLS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "MyTaxFiling API"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
