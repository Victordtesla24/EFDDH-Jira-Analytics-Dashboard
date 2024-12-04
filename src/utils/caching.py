import functools
import json
from typing import Any, Callable, Dict, TypeVar

T = TypeVar("T")


def cache_data(ttl: int = 3600) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache function results with TTL."""
    cache: Dict[str, Any] = {}

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create a stable cache key by sorting kwargs
            key_parts = []
            if args:
                key_parts.append(str(args))
            if kwargs:
                # Sort kwargs by key to ensure consistent ordering
                sorted_kwargs = dict(sorted(kwargs.items()))
                key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))

            cache_key = "|".join(key_parts)

            if cache_key not in cache:
                cache[cache_key] = func(*args, **kwargs)
            return cache[cache_key]

        return wrapper

    return decorator
