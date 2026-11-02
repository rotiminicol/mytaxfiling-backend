from supabase import create_client, Client
from app.core.config import settings

supabase_admin: Client = None
if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_admin = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
    except Exception as e:
        print(f"Warning: Failed to initialize supabase_admin: {e}")

supabase_anon: Client = None
if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
    try:
        supabase_anon = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    except Exception as e:
        print(f"Warning: Failed to initialize supabase_anon: {e}")
