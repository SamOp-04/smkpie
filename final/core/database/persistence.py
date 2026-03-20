"""
Database persistence service for saving predictions, alerts, logs, and metrics.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from core.database.supabase import supabase
import logging


class PersistenceService:
    """Handles all database write operations for predictions, alerts, logs, and metrics"""

    @staticmethod
    async def save_prediction(
        user_id: str,
        api_key: str,
        input_data: Dict[str, Any],
        score: float,
        is_anomaly: bool,
        action: str,
        processing_time_ms: int,
        model_version: Optional[str] = None
    ) -> int:
        """Save prediction to database"""
        try:
            result = supabase.table('predictions').insert({
                'user_id': user_id,
                'api_key': api_key,
                'input_data': input_data,
                'score': score,
                'is_anomaly': is_anomaly,
                'recommended_action': action,
                'processing_time_ms': processing_time_ms,
                'model_version': model_version or 'v1.0'
            }).execute()
            return result.data[0]['id'] if result.data else 0
        except Exception as e:
            logging.error(f"Failed to save prediction: {e}")
            return 0

    @staticmethod
    async def save_alert(
        user_id: str,
        prediction_id: int,
        alert_type: str,
        severity: str,
        score: float,
        payload: Dict[str, Any],
        status: str = 'pending',
        error_message: Optional[str] = None
    ) -> int:
        """Save alert to database"""
        try:
            result = supabase.table('alerts').insert({
                'user_id': user_id,
                'prediction_id': prediction_id,
                'alert_type': alert_type,
                'severity': severity,
                'score': score,
                'payload': payload,
                'status': status,
                'error_message': error_message
            }).execute()
            return result.data[0]['id'] if result.data else 0
        except Exception as e:
            logging.error(f"Failed to save alert: {e}")
            return 0

    @staticmethod
    async def save_api_log(
        user_id: Optional[str],
        api_key: Optional[str],
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        error_message: Optional[str] = None
    ):
        """Save API log to database"""
        try:
            supabase.table('api_logs').insert({
                'user_id': user_id,
                'api_key': api_key,
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time_ms': response_time_ms,
                'error_message': error_message
            }).execute()
        except Exception as e:
            logging.error(f"Failed to save API log: {e}")

    @staticmethod
    async def save_performance_metric(
        user_id: str,
        metric_type: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save performance metric to database"""
        try:
            supabase.table('performance_metrics').insert({
                'user_id': user_id,
                'metric_type': metric_type,
                'metric_value': metric_value,
                'metadata': metadata
            }).execute()
        except Exception as e:
            logging.error(f"Failed to save performance metric: {e}")

    @staticmethod
    def get_severity_from_score(score: float) -> str:
        """Determine alert severity based on anomaly score"""
        if score >= 0.95:
            return "critical"
        elif score >= 0.75:
            return "high"
        elif score >= 0.5:
            return "medium"
        return "low"
