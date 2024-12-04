import time
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Always make at least one attempt
            attempts = max(1, max_attempts)
            last_exception = None

            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < attempts - 1:
                        # Use the actual delay value, even if negative
                        time.sleep(delay * (2**attempt))

            if last_exception:
                raise last_exception
            raise RuntimeError("All retry attempts failed")

        return wrapper

    return decorator
