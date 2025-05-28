from supabase import Client
from core.config import settings

class RealtimeNotifier:
    def __init__(self):
        self.client = Client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
    def send_alert(self, user_id: str, message: str):
        self.client.channel('alerts').send({
            'type': 'broadcast',
            'event': 'security_alert',
            'payload': {
                'user_id': user_id,
                'message': message
            }
        })