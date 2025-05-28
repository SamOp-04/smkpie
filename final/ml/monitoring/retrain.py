from celery import shared_task
from ml.training.train import train_cyber_model
from core.database import supabase

@shared_task
def trigger_retraining(user_id: str):
    try:
        train_cyber_model()
        supabase.table('model_versions').insert({
            'user_id': user_id,
            'status': 'deployed'
        }).execute()
    except Exception as e:
        supabase.table('model_versions').insert({
            'user_id': user_id,
            'status': 'failed',
            'error': str(e)
        }).execute()