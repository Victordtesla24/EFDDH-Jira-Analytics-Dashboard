from .core import AutoErrorHandler
from .runtime_manager import RuntimeManager, WebInterfaceProtocol
from .web_interface import WebInterface, RuntimeManagerProtocol
from .error_handler import ErrorHandler
from .dependency_manager import DependencyManager
from .package_manager import PackageManager
from .ai_service import AIService
from .fix_processor import FixProcessor
from .logging_config import setup_logging

__version__ = '1.0.0'
__all__ = [
    "AutoErrorHandler",
    "RuntimeManager",
    "WebInterface",
    "RuntimeManagerProtocol",
    "WebInterfaceProtocol",
    "ErrorHandler",
    "DependencyManager",
    'PackageManager',
    'AIService',
    'FixProcessor',
    'setup_logging'
]