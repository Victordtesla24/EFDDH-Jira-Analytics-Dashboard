from typing import Dict, Any, Optional, Protocol
from .dependency_manager import DependencyManager
from .error_handler import ErrorHandler
from .logging_config import setup_logging

class WebInterfaceProtocol(Protocol):
    async def start(self): ...
    async def handle_websocket(self, websocket: Any): ...

class RuntimeManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.dependency_manager = DependencyManager()
        self.error_handler = ErrorHandler()
        self.logger = setup_logging('RuntimeManager')
        self._web_interface = None

    def register_web_interface(self, web_interface: WebInterfaceProtocol):
        self._web_interface = web_interface

    async def initialize(self):
        try:
            if not self.dependency_manager.install_missing():
                raise RuntimeError("Failed to install required dependencies")
            return True
        except Exception as e:
            await self.error_handler.handle_error(e, {"context": "initialization"})
            raise

    async def process_request(self, message: str) -> str:
        """Process incoming requests from web interface"""
        try:
            # Basic command processing
            if message.startswith("/"):
                return await self._handle_command(message[1:])
            
            # Normal message processing
            return f"Processed: {message}"
            
        except Exception as e:
            error_msg = await self.error_handler.handle_error(e, {"message": message})
            return error_msg or "An error occurred processing your request"

    async def _handle_command(self, command: str) -> str:
        """Handle special commands"""
        commands = {
            "status": self._get_status,
            "help": self._get_help,
            "description": self._get_description
        }
        
        cmd = command.split()[0]
        if cmd in commands:
            return await commands[cmd]()
        return f"Unknown command: {cmd}"

    async def _get_status(self) -> str:
        """Get system status"""
        deps = self.dependency_manager.check_dependencies()
        return f"System Status:\nDependencies: {all(deps.values())}"

    async def _get_help(self) -> str:
        """Get help information"""
        return """Available commands:
        /status - Check system status
        /help - Show this help message
        /description - Show AI assistant description"""

    async def _get_description(self) -> str:
        """Get AI assistant description"""
        return """AI Assistant Description:
        This AI assistant is designed to help with resume optimization, job description analysis, 
        and automated error handling using advanced AI models. It integrates various services 
        to provide comprehensive support for job seekers and developers."""