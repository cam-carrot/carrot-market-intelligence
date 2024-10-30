import functools
import asyncio
import logging
from typing import Callable
from httpx import RequestError

logger = logging.getLogger(__name__)

def handle_api_error(func: Callable):
    """Decorator to handle API errors consistently."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RequestError as e:
            logger.error(f"API error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    return wrapper

async def rate_limit_decorator(func: Callable, delay: float = 1.0):
    """Decorator to implement rate limiting."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        await asyncio.sleep(delay)
        return await func(*args, **kwargs)
    return wrapper