from functools import wraps
from sentry_sdk import start_transaction
from typing import Callable


def with_transaction(name: str, op: str = "request"):
    """
    Begin a transaction in Sentry
    :param name: the name of the transaction
    :param op: the operation occurring in the transaction
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with start_transaction(name=name, op=op):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
