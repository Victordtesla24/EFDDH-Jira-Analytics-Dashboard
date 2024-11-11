import json
import logging
import openai
from typing import Optional, Dict, Any

class AIService:
    ERROR_CATEGORIES = {
        'ImportError': 'dependency',
        'ModuleNotFoundError': 'dependency',
        'SyntaxError': 'code',
        'TypeError': 'code',
        'ValueError': 'validation',
        'RuntimeError': 'runtime',
        'EnvironmentError': 'environment'
    }

    def __init__(self, api_key: str, logger: logging.Logger):
        self.api_key = api_key
        openai.api_key = api_key
        self.logger = logger

    def get_fix(self, prompt: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get fix or optimization suggestion from AI."""
        models = ["gpt-4", "gpt-3.5-turbo"]
        
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                return self._parse_response(response.choices[0].message.content)
            except Exception as e:
                self.logger.error(f"AI suggestion failed for model {model}: {str(e)}")
        
        return None

    def _create_fix_prompt(self, error: Exception, context: Dict[str, Any]) -> str:
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

    @staticmethod
    def _get_system_prompt() -> str:
        return """You are an expert Python developer assistant.
        Analyze errors and provide specific fix instructions in JSON format.
        Only suggest fixes that are safe and follow best practices."""

    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        return "\n".join(f"{k}: {v}" for k, v in context.items())

    @staticmethod
    def _parse_response(response: str) -> Optional[Dict[str, Any]]:
        if not response:
            return None
            
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end <= start:
                return None
                
            json_str = response[start:end]
            result = json.loads(json_str)
            
            return result if isinstance(result, dict) else None
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse AI response: {str(e)}")
            return None