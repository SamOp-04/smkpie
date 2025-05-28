# core/database/supabase_crud.py

from supabase import create_client, Client
from core.config import settings
from uuid import uuid4

class SupabaseCRUD:
    def __init__(self):
        # Initialize Supabase client with service role key for full access
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

    def create_user(self, email: str, password: str):
        try:
            # 1️⃣ Create in Supabase Auth
            response = self.client.auth.sign_up({
                'email': email,
                'password': password
            })
            if not response.user:
                raise Exception(f"Auth signup failed: {response.error}")

            user_id = response.user.id

            # 2️⃣ Generate your own API token
            api_token = str(uuid4())

            # 3️⃣ Insert into your public.users table
            self.client.table('users').insert({
                'id': user_id,
                'email': email,
                'api_token': api_token
            }).execute()

            # 4️⃣ Return a custom object (not Supabase's User)
            return {
                "id": user_id,
                "email": email,
                "api_token": api_token
            }

        except Exception as e:
            raise Exception(f"Error creating user: {e}")


    def authenticate_user(self, email: str, password: str):
        try:
            response = self.client.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            if response.user:
                # Fetch stored api_token
                rec = self.client.table('users').select('api_token').eq('id', response.user.id).execute()
                if rec.data:
                    return {
                        "id": response.user.id,
                        "email": email,
                        "api_token": rec.data[0]['api_token']
                    }
                else:
                    raise Exception("API token not found")
            else:
                raise Exception("Invalid credentials")
        except Exception as e:
            raise Exception(f"Error authenticating user: {e}")


    def get_user_by_token(self, token: str):
        try:
            # Lookup user by api_token column
            response = self.client.table('users').select('*').eq('api_token', token).execute()
            if response.data:
                return response.data[0]
            else:
                raise Exception("User not found with given token")
        except Exception as e:
            raise Exception(f"Error fetching user by token: {e}")

    def user_exists_by_email(self, email: str):
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return bool(response.data)
        except Exception as e:
            raise Exception(f"Error checking user existence: {e}")

    def update_user(self, user_id: str, updated_data: dict):
        try:
            response = self.client.table('users').update(updated_data).eq('id', user_id).execute()
            if not response.data:
                raise Exception("User not found or update failed")
            return response.data[0]
        except Exception as e:
            raise Exception(f"Error updating user: {e}")

    def create_or_update_api_token(self, user_id: str):
        try:
            api_token = str(uuid4())
            response = self.client.table('users').update({'api_token': api_token}).eq('id', user_id).execute()
            if not response.data:
                raise Exception("User not found or API token update failed")
            return api_token
        except Exception as e:
            raise Exception(f"Error creating/updating API token: {e}")
    def upsert_monitor_settings(self, user_id: str, settings_data: dict):
        try:
            # Explicitly set 'on_conflict' to handle duplicate user_id
            response = self.client.table('monitor_settings') \
                .upsert({
                    'user_id': user_id,
                    **settings_data
                }, on_conflict=["user_id"]) \
                .execute()
            
            if not response.data:
                raise Exception("Upsert failed")

            return response.data[0]
        except Exception as e:
            raise Exception(f"Error upserting monitor settings: {e}")
    def invalidate_token(self, token: str):
        try:
            # Find the user by the current token
            response = self.client.table('users').select('id').eq('api_token', token).execute()
            if not response.data:
                raise Exception("Invalid or expired token")

            user_id = response.data[0]['id']

            # Invalidate the token by replacing it with a new random one
            new_token = str(uuid4())
            self.client.table('users').update({'api_token': new_token}).eq('id', user_id).execute()

            return True
        except Exception as e:
            raise Exception(f"Error invalidating token: {e}")

