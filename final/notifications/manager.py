"""
Unified notification manager that orchestrates alerts across all channels.
"""

from typing import List, Dict, Any
import asyncio
import logging
from notifications.email import send_email_alert
from notifications.webhooks import send_webhook
from notifications.supabase_realtime import RealtimeNotifier
from core.database.persistence import PersistenceService


class NotificationManager:
    """Orchestrates notifications across webhook, email, and realtime channels"""

    def __init__(self):
        self.realtime_notifier = RealtimeNotifier()

    async def send_alert(
        self,
        user_id: str,
        prediction_id: int,
        score: float,
        action: str,
        user_email: str,
        notification_channels: List[str]
    ):
        """
        Send alerts through all configured channels.

        Args:
            user_id: User UUID
            prediction_id: ID of the prediction that triggered the alert
            score: Anomaly score
            action: Recommended action (allow/monitor/throttle/block)
            user_email: User's email address
            notification_channels: List of channels to use: ['webhook', 'email', 'realtime']
        """
        severity = PersistenceService.get_severity_from_score(score)

        payload = {
            "anomaly": True,
            "score": score,
            "recommended_action": action,
            "prediction_id": prediction_id,
            "severity": severity
        }

        # Send webhook notification
        if 'webhook' in notification_channels:
            try:
                await send_webhook(user_id=user_id, payload=payload)
                await PersistenceService.save_alert(
                    user_id=user_id,
                    prediction_id=prediction_id,
                    alert_type='webhook',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='sent'
                )
                logging.info(f"✓ Webhook alert sent for prediction {prediction_id}")
            except Exception as e:
                logging.warning(f"✗ Webhook alert failed for prediction {prediction_id}: {e}")
                await PersistenceService.save_alert(
                    user_id=user_id,
                    prediction_id=prediction_id,
                    alert_type='webhook',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='failed',
                    error_message=str(e)
                )

        # Send email notification
        if 'email' in notification_channels:
            try:
                # Send email in thread pool to avoid blocking
                await asyncio.to_thread(send_email_alert, user_email, score)
                await PersistenceService.save_alert(
                    user_id=user_id,
                    prediction_id=prediction_id,
                    alert_type='email',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='sent'
                )
                logging.info(f"✓ Email alert sent for prediction {prediction_id}")
            except Exception as e:
                logging.warning(f"✗ Email alert failed for prediction {prediction_id}: {e}")
                await PersistenceService.save_alert(
                    user_id=user_id,
                    prediction_id=prediction_id,
                    alert_type='email',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='failed',
                    error_message=str(e)
                )

        # Send realtime notification
        if 'realtime' in notification_channels:
            try:
                message = f"Anomaly detected! Score: {score:.2f}, Action: {action}, Severity: {severity}"
                self.realtime_notifier.send_alert(user_id=user_id, message=message)
                await PersistenceService.save_alert(
                    user_id=user_id,
                    prediction_id=prediction_id,
                    alert_type='realtime',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='sent'
                )
                logging.info(f"✓ Realtime alert sent for prediction {prediction_id}")
            except Exception as e:
                logging.warning(f"✗ Realtime alert failed for prediction {prediction_id}: {e}")
                await PersistenceService.save_alert(
                    user_id=user_id,
                    prediction_id=prediction_id,
                    alert_type='realtime',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='failed',
                    error_message=str(e)
                )
