import logging
import openai
from typing import Optional, Dict, Any
import json

class AIService:
    def __init__(self, api_key: str, logger: logging.Logger):
        """Initialize AI Service with OpenAI API key."""
        self.api_key = api_key
        openai.api_key = api_key
        self.logger = logger
        
        # Verify API key
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Test API connection
        try:
            openai.Model.list()
        except Exception as e:
            self.logger.error(f"OpenAI API initialization failed: {str(e)}")
            raise ValueError(f"OpenAI API initialization failed: {str(e)}")

    def get_fix(self, prompt: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API call to get AI suggestions/fixes.
        
        Args:
            prompt (str): The prompt to send to the AI
            context (Dict[str, Any]): Additional context for the prompt
            
        Returns:
            Optional[Dict[str, Any]]: Response from AI or None if failed
        """
        try:
            self.logger.debug("Making OpenAI API request")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": self._format_prompt(prompt, context)
                }]
            )
            
            content = response.choices[0].message.content
            self.logger.debug(f"Received response: {content[:100]}...")
            
            try:
                if isinstance(content, str):
                    parsed = json.loads(content)
                else:
                    parsed = content
                
                return {
                    "match_score": parsed.get("match_score", 70),
                    "matching_skills": parsed.get("matching_skills", []),
                    "missing_skills": parsed.get("missing_skills", []),
                    "improvement_suggestions": parsed.get("improvement_suggestions", []),
                    "keywords_to_add": parsed.get("keywords_to_add", [])
                }
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing error: {str(e)}")
                return {
                    "match_score": 70,
                    "matching_skills": [],
                    "missing_skills": [],
                    "improvement_suggestions": [content],
                    "keywords_to_add": []
                }
                
        except Exception as e:
            self.logger.error(f"AI Service error: {str(e)}")
            raise
            
    def _format_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Format the prompt with context.
        
        Args:
            prompt (str): Base prompt
            context (Dict[str, Any]): Context to include
            
        Returns:
            str: Formatted prompt
        """
        formatted_context = "\n".join(f"{k}: {v}" for k, v in context.items())
        return f"{prompt}\n\nContext:\n{formatted_context}"