from core.database import supabase

def run_migrations():
    supabase.rpc('''
    CREATE TABLE IF NOT EXISTS model_versions (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id),
        version VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW()
    );
    ''').execute()