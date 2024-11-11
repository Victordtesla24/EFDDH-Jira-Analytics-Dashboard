import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .package_manager import PackageManager
from .logging_config import setup_logging
from .ai_service import AIService
from .fix_processor import FixProcessor

class AutoErrorHandler:
    def __init__(self, api_key: str, max_retries: int = 3):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.max_retries = max_retries
        self.logger = setup_logging('AutoErrorHandler')
        self.package_manager = PackageManager(self.logger)
        self.ai_service = AIService(api_key, self.logger)
        self.fix_processor = FixProcessor(self.logger)
        self._validate_environment()

    def _validate_environment(self):
        """Validate and setup environment requirements"""
        required_dirs = ['logs', 'fixes', 'backups']
        for dir_name in required_dirs:
            Path(dir_name).mkdir(exist_ok=True)
            
        # Validate Python version
        if sys.version_info < (3, 8):
            raise EnvironmentError("Python 3.8 or higher is required")
        # Validate key environment variables
        required_env_vars = ['OPENAI_API_KEY', 'LOG_LEVEL']
        for var in required_env_vars:
            if not os.getenv(var):
                self.logger.warning(f"Missing environment variable: {var}")

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        if not context:
            context = {}  # Ensure context is always a dict
        self.logger.error(f"Error occurred: {str(error)}")
        self.logger.debug(f"Error context: {context}")
        
        # Add error context enrichment
        context['python_version'] = sys.version
        context['platform'] = sys.platform
        context['timestamp'] = datetime.now().isoformat()
        
        for attempt in range(self.max_retries):
            self.logger.info(f"Fix attempt {attempt + 1}/{self.max_retries}")
            
            # Handle import errors directly
            if isinstance(error, ImportError):
                if self.package_manager.handle_import_error(str(error)):
                    return True
                continue

            # Get and apply AI fix
            fix = self.ai_service.get_fix(error, context)
            if fix and self.fix_processor.apply_fix(fix, context):
                self.logger.info("Fix applied successfully")
                return True
                
        self.logger.error("Failed to fix error after maximum retries")
        return False