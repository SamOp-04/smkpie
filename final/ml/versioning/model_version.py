from core.database import supabase

class ModelVersioner:
    def track_version(self, user_id: str, version: str):
        supabase.table('model_versions').insert({
            'user_id': user_id,
            'version': version
        }).execute()