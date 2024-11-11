import logging
from typing import Dict, Any, Set
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import openai

logger = logging.getLogger(__name__)

class AIResumeWriter:
    """AI-powered resume writing and tailoring"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer()
        
    def tailor_resume(self, original_resume: str, job_desc: str, metrics: Dict[str, Any]) -> str:
        """Generate tailored resume using AI."""
        prompt = self._create_tailoring_prompt(original_resume, job_desc, metrics)
        
        try:
            response = self.ai_service.get_fix(prompt, {"original_resume": original_resume, "job_desc": job_desc, "metrics": metrics})
            return response if response else original_resume
        except Exception as e:
            logger.error(f"AI resume tailoring failed: {str(e)}")
            return original_resume

    def _get_system_prompt(self) -> str:
        return """You are an expert resume writer with deep knowledge of ATS systems and 
        industry best practices. Your task is to tailor resumes to specific job descriptions
        while maintaining professional standards and authenticity."""

    def _create_tailoring_prompt(self, resume: str, job_desc: str, metrics: Dict[str, Any]) -> str:
        return f"""Tailor this resume for the job description, following these guidelines:
        1. Emphasize matching skills: {metrics.get('matching_skills', [])}
        2. Add missing relevant skills: {metrics.get('missing_skills', [])}
        3. Adjust experience descriptions to highlight relevant achievements
        4. Use industry-standard keywords: {self._extract_industry_keywords(job_desc)}
        5. Maintain ATS-friendly formatting
        6. Ensure all claims are truthful and based on the original resume
        
        Original Resume:
        {resume}
        
        Job Description:
        {job_desc}
        
        Match Score: {metrics.get('match_score', 0)}
        
        Output Format: Professional resume in markdown format"""

    def _extract_industry_keywords(self, text: str) -> Set[str]:
        """Extract industry-specific keywords"""
        doc = self.nlp(text)
        return {token.text for token in doc if token.pos_ in {'NOUN', 'PROPN'} and len(token.text) > 2}