import logging
from typing import Any, Protocol
from datetime import timedelta


class ActionExecutor(Protocol):
    async def execute(self, action: str, context: dict[str, Any]) -> None:
        ...


class LoggingActionExecutor:
    """Logs actions only (default, no actual enforcement)"""
    async def execute(self, action: str, context: dict[str, Any]) -> None:
        logging.info("Action executor invoked: action=%s context=%s", action, context)


class RedisActionExecutor:
    """Executes defensive actions by storing state in Redis"""

    async def execute(self, action: str, context: dict[str, Any]) -> None:
        from core.database.redis_manager import redis_manager

        api_key = context.get('api_key')
        user_id = context.get('user_id')
        score = context.get('score', 0)

        if not api_key:
            logging.warning("No api_key in context, cannot execute action")
            return

        redis = await redis_manager.get_connection()

        if action == 'block':
            # Block API key for 1 hour
            await redis.setex(f"blocked:{api_key}", timedelta(hours=1), "1")
            logging.warning(f"🚫 BLOCKED api_key={api_key} (score={score:.2f}) for 1 hour")

        elif action == 'throttle':
            # Throttle API key for 15 minutes
            await redis.setex(f"throttled:{api_key}", timedelta(minutes=15), "1")
            logging.warning(f"⚠️ THROTTLED api_key={api_key} (score={score:.2f}) for 15 minutes")

        elif action == 'monitor':
            # Increment monitoring counter
            count = await redis.incr(f"monitor:{api_key}")
            logging.info(f"👁️ MONITORING api_key={api_key} (count={count}, score={score:.2f})")

        elif action == 'allow':
            # No enforcement needed
            logging.info(f"✓ ALLOWED api_key={api_key} (score={score:.2f})")


_action_executor: ActionExecutor = LoggingActionExecutor()


def set_action_executor(executor: ActionExecutor) -> None:
    global _action_executor
    _action_executor = executor


async def execute_action(action: str, context: dict[str, Any]) -> None:
    await _action_executor.execute(action, context)
