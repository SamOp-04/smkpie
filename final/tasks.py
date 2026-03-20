from celery import shared_task
from ml.monitoring.retrain import trigger_retraining
from core.database.supabase import supabase
from core.database.persistence import PersistenceService
import logging


@shared_task
def check_model_performance():
    """Check model performance on recent predictions (last 24 hours)"""
    try:
        # Query recent predictions from database
        predictions = supabase.table('predictions')\
            .select('score, is_anomaly')\
            .gte('timestamp', 'now() - interval \'24 hours\'')\
            .execute()

        if not predictions.data or len(predictions.data) < 100:
            logging.info(f"Not enough predictions for performance check (found {len(predictions.data) if predictions.data else 0})")
            return

        # Calculate basic metrics
        total = len(predictions.data)
        anomalies = sum(1 for p in predictions.data if p['is_anomaly'])
        anomaly_rate = anomalies / total if total > 0 else 0
        avg_score = sum(p['score'] for p in predictions.data) / total if total > 0 else 0

        logging.info(f"Performance check: {total} predictions, {anomalies} anomalies ({anomaly_rate:.2%}), avg_score={avg_score:.3f}")

        # Save metrics to database (synchronous for Celery)
        # Note: PersistenceService methods are async, would need sync wrapper in production
        # For now, just log the metrics
        logging.info(f"Model performance metrics calculated: anomaly_rate={anomaly_rate:.3f}, avg_score={avg_score:.3f}")

    except Exception as e:
        logging.error(f"Performance check failed: {e}")


@shared_task
def evaluate_retraining_need():
    """Evaluate if model retraining is needed based on performance degradation"""
    try:
        # Query recent performance metrics
        metrics = supabase.table('performance_metrics')\
            .select('metric_type, metric_value')\
            .gte('timestamp', 'now() - interval \'7 days\'')\
            .eq('metric_type', 'accuracy')\
            .execute()

        if not metrics.data or len(metrics.data) == 0:
            logging.info("No recent performance metrics found, skipping retraining evaluation")
            return

        # Calculate average accuracy over last 7 days
        avg_accuracy = sum(m['metric_value'] for m in metrics.data) / len(metrics.data)

        # Trigger retraining if performance degraded
        ACCURACY_THRESHOLD = 0.85
        if avg_accuracy < ACCURACY_THRESHOLD:
            logging.warning(f"Model performance degraded (accuracy: {avg_accuracy:.3f} < {ACCURACY_THRESHOLD}), triggering retraining")
            trigger_retraining.delay('system')
        else:
            logging.info(f"Model performance acceptable (accuracy: {avg_accuracy:.3f})")

    except Exception as e:
        logging.error(f"Retraining evaluation failed: {e}")