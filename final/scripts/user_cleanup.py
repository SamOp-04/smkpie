from core.database import supabase
from core.config import settings

def cleanup_inactive_users(days=30):
    query = f"""
    DELETE FROM users
    WHERE last_login < NOW() - INTERVAL '{days} days'
    RETURNING id;
    """
    result = supabase.rpc('execute_sql', {'query': query}).execute()
    return result.data