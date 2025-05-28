from supabase import create_client, Client
from core.config import settings

# Create a Supabase client instance using your settings
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)