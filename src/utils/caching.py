import functools
from typing import Any, Callable, Dict, TypeVar

T = TypeVar("T")


def cache_data(ttl: int = 3600) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache function results with TTL."""
    cache: Dict[str, Any] = {}

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_key = str(args) + str(kwargs)
            if cache_key not in cache:
                cache[cache_key] = func(*args, **kwargs)
            return cache[cache_key]

        return wrapper

    return decorator
