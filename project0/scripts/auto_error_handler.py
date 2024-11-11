import sys
import subprocess
import logging
import json
import openai
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from auto_error_handler import AutoErrorHandler

class AutoErrorHandler:
    """Automated error handling and fixing system with AI integration"""
    
    def __init__(self, api_key: str, max_retries: int = 3):
        """Initialize error handler
        
        Args:
            api_key: OpenAI API key
            max_retries: Maximum retry attempts for fixes
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.logger = self._setup_logging()
        openai.api_key = api_key

    PACKAGE_MAPPING = {
        'spacy': ['spacy', 'en-core-web-sm'],
        'sklearn': ['scikit-learn'],
        'sklearn.feature_extraction.text': ['scikit-learn'],  
    }

    def handle_import_error(self, module_name: str) -> bool:
        """Handle import-related errors by installing required packages"""
        if not module_name:
            self.logger.error("Empty module name provided")
            return False

        self.logger.info(f"Handling import error for module: {module_name}")
        
        try:
            # Get required packages
            packages = self.PACKAGE_MAPPING.get(module_name, [module_name])
            
            # Install packages
            if not self._fix_pip_install(packages):
                return False
                
            # Special handling for spacy
            if module_name == 'spacy':
                return self._handle_spacy_installation()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to handle import error: {str(e)}")
            return False

    def _handle_spacy_installation(self) -> bool:
        """Handle spacy-specific installation requirements"""
        try:
            import spacy
            if not spacy.util.is_package('en_core_web_sm'):
                self.logger.info("Installing spacy language model")
                subprocess.check_call([
                    sys.executable, 
                    "-m", 
                    "spacy",
                    "download",
                    "en_core_web_sm"
                ])
            return True
        except Exception as e:
            self.logger.error(f"Failed to install spacy language model: {str(e)}")
            return False

    def _setup_logging(self) -> logging.Logger:
        """Configure logging"""
        logger = logging.getLogger('AutoErrorHandler')
        logger.setLevel(logging.DEBUG)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            
            # File handler
            fh = logging.FileHandler('error_handler.log')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            
            logger.addHandler(ch)
            logger.addHandler(fh)
        
        return logger

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Main error handling method
        
        Args:
            error: The exception that occurred
            context: Dictionary with contextual information
            
        Returns:
            bool: True if error was fixed, False otherwise
        """
        self.logger.error(f"Error occurred: {str(error)}")
        self.logger.debug(f"Error context: {context}")
        
        for attempt in range(self.max_retries):
            self.logger.info(f"Fix attempt {attempt + 1}/{self.max_retries}")
            
            # Get AI suggestion
            fix = self._get_ai_fix(error, context)
            if not fix:
                continue
                
            # Apply fix
            if self._apply_fix(fix, context):
                self.logger.info("Fix applied successfully")
                return True
                
        self.logger.error("Failed to fix error after maximum retries")
        return False

    def _get_ai_fix(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get fix suggestion from AI"""
        # Add import error handling first
        if isinstance(error, ImportError):
            module_name = str(error).split("'")[1] if "'" in str(error) else str(error)
            if self.handle_import_error(module_name):
                return {"type": "import_fix", "module": module_name}

        prompt = self._create_fix_prompt(error, context)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            fix_json = self._parse_ai_response(response.choices[0].message.content)
            if not self._validate_fix_instructions(fix_json):
                self.logger.error("Invalid fix instructions from AI")
                return None
                
            return fix_json
            
        except Exception as e:
            self.logger.error(f"AI suggestion failed: {str(e)}")
            return None
            
    def _validate_fix_instructions(self, fix: Optional[Dict[str, Any]]) -> bool:
        """Validate fix instructions format"""
        if not isinstance(fix, dict) or 'type' not in fix:
            return False
            
        required_fields = {
            'pip_install': ['packages'],
            'env_setup': ['commands'],
            'code_fix': ['file', 'changes'],
            'import_fix': ['module']
        }
        
        fix_type = fix.get('type')
        if fix_type not in required_fields:
            return False
            
        # Validate required fields exist and are of correct type
        for field in required_fields[fix_type]:
            if field not in fix:
                return False
            
            # Type-specific validation
            if field == 'packages' and not isinstance(fix['packages'], list):
                return False
            elif field == 'commands' and not isinstance(fix['commands'], list):
                return False
            elif field == 'changes' and not isinstance(fix['changes'], list):
                return False
                
        return True

    def _apply_fix(self, fix: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Apply suggested fix
        
        Args:
            fix: Fix instructions from AI
            context: Error context
            
        Returns:
            bool: True if fix was applied successfully
        """
        try:
            fix_type = fix.get('type')
            if fix_type == 'pip_install':
                return self._fix_pip_install(fix['packages'])
            elif fix_type == 'env_setup':
                return self._fix_env_setup(fix['commands'])
            elif fix_type == 'code_fix':
                return self._fix_code(fix['file'], fix['changes'])
            else:
                self.logger.error(f"Unknown fix type: {fix_type}")
                return False
        except Exception as e:
            self.logger.error(f"Fix application failed: {str(e)}")
            return False

    def _fix_pip_install(self, packages: List[str]) -> bool:
        """Fix pip installation issues"""
        try:
            for package in packages:
                self.logger.info(f"Installing {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            return True
        except Exception as e:
            self.logger.error(f"Package installation failed: {str(e)}")
            return False

    def _fix_env_setup(self, commands: List[str]) -> bool:
        """Fix environment setup issues"""
        try:
            for cmd in commands:
                self.logger.info(f"Running: {cmd}")
                subprocess.check_call(cmd, shell=True)
            return True
        except Exception as e:
            self.logger.error(f"Environment setup failed: {str(e)}")
            return False

    def _fix_code(self, file_path: str, changes: List[Dict[str, Any]]) -> bool:
        """Apply code fixes to a file
        
        Args:
            file_path: Path to file needing fixes
            changes: List of changes to apply, each with 'line' and 'code' keys
            
        Returns:
            bool: True if fixes were applied successfully
        """
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False

            with open(path, 'r') as file:
                lines = file.readlines()

            for change in changes:
                line_num = change.get('line', 0)
                new_code = change.get('code', '')
                if 0 <= line_num < len(lines):
                    lines[line_num] = new_code + '\n'

            with open(path, 'w') as file:
                file.writelines(lines)
            return True
            
        except Exception as e:
            self.logger.error(f"Code fix failed: {str(e)}")
            return False

    def _create_fix_prompt(self, error: Exception, context: Dict[str, Any]) -> str:
        """Create prompt for AI fix suggestion"""
        return f"""Please analyze this error and suggest a fix:
        
        Error: {str(error)}
        Type: {type(error).__name__}
        Context: {self._format_context(context)}
        
        Provide fix instructions in JSON format:
        {{
            "type": "pip_install|env_setup|code_fix",
            "packages": ["pkg1", "pkg2"],  # for pip_install
            "commands": ["cmd1", "cmd2"],  # for env_setup
            "file": "path/to/file",        # for code_fix
            "changes": [                   # for code_fix
                {{"line": 123, "code": "new code"}}
            ]
        }}"""

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI model"""
        return """You are an expert Python developer assistant.
        Analyze errors and provide specific fix instructions in JSON format.
        Only suggest fixes that are safe and follow best practices."""

    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        """Format context information"""
        return "\n".join(f"{k}: {v}" for k, v in context.items())

    @staticmethod
    def _parse_ai_response(response: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into fix instructions"""
        if not response:
            return None
            
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end <= start:
                return None
                
            json_str = response[start:end]
            result = json.loads(json_str)
            
            # Ensure result is a dictionary
            return result if isinstance(result, dict) else None
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse AI response: {str(e)}")
            return None