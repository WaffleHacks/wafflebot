from functools import wraps
from sentry_sdk import start_transaction
from typing import Callable


def with_transaction(name: str):
    """
    Begin a transaction in Sentry
    :param name: the name of the transaction
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with start_transaction(name=name, op="request"):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
