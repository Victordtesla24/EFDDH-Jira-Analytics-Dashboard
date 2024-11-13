import logging
from functools import wraps
from typing import Callable, Any

class ErrorHandler:
    @staticmethod
    def handle_errors(default_return: Any = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error in {func.__name__}: {str(e)}")
                    return default_return
            return wrapper
        return decorator
