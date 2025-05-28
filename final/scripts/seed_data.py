from core.database import supabase

def seed_initial_users():
    supabase.table('users').insert([{
        'email': 'admin@example.com',
        'encrypted_password': '...',
        'role': 'admin'
    }]).execute()