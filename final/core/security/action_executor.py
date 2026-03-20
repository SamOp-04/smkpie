import logging
from typing import Any, Protocol


class ActionExecutor(Protocol):
    async def execute(self, action: str, context: dict[str, Any]) -> None:
        ...


class LoggingActionExecutor:
    async def execute(self, action: str, context: dict[str, Any]) -> None:
        logging.info("Action executor invoked: action=%s context=%s", action, context)


_action_executor: ActionExecutor = LoggingActionExecutor()


def set_action_executor(executor: ActionExecutor) -> None:
    global _action_executor
    _action_executor = executor


async def execute_action(action: str, context: dict[str, Any]) -> None:
    await _action_executor.execute(action, context)
