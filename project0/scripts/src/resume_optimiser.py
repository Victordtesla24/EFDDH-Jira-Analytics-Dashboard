import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from pypdf import PdfReader
from docx import Document
import openai

from job_scraper import JobScraper
from ai_resume_writer import AIResumeWriter
from resume_formatter import ResumeFormatter
from resume_analytics import ResumeAnalytics
from ai_service import AIService

logger = logging.getLogger(__name__)

class ResumeOptimizer:
    ANALYSIS_PROMPT = """Please analyze this resume against the job description:

Resume:
{resume}

Job Description:
{job_description}

Provide detailed analysis of the match and specific improvement suggestions."""

    def __init__(self, api_key: str):
        """Initialize the Resume Optimizer."""
        self._validate_api_key(api_key)
        self.api_key = api_key
        self.ai_service = AIService(api_key, logger)
        self._reset_state()
        self.job_scraper = JobScraper()
        self.ai_writer = AIResumeWriter(api_key)
        self.logger = logging.getLogger(__name__)
        
    def _reset_state(self) -> None:
        """Reset internal state"""
        self.original_resume = ""
        self.job_description = ""
        
    def _validate_api_key(self, api_key: str) -> None:
        """Validate API key"""
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Valid API key required")
            
    def read_pdf_resume(self, file_path: str) -> bool:
        """Read and extract text from PDF resume."""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        if path.suffix.lower() != '.pdf':
            logger.error(f"Invalid file format: {path.suffix}")
            return False
            
        try:
            with open(path, 'rb') as file:
                reader = PdfReader(file)
                self.original_resume = "\n".join(page.extract_text() for page in reader.pages)
            return True
        except Exception as e:
            logger.exception(f"Error reading PDF: {str(e)}")
            return False

    def check_pdf_exists(self, file_path: str) -> bool:
        """Check if PDF file exists at the specified path.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            bool: True if file exists and is PDF, False otherwise
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"PDF file not found at: {file_path}")
            return False
        
        if path.suffix.lower() != '.pdf':
            logger.error(f"File exists but is not a PDF: {file_path}")
            return False
            
        logger.info(f"PDF file found at: {file_path}")
        return True

    def get_job_description(self) -> bool:
        """Get job description from user input.
        
        Returns:
            bool: True if job description was provided, False otherwise
        """
        print("\nPlease paste the job description (press Ctrl+D or Ctrl+Z when finished):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            self.job_description = '\n'.join(lines).strip()
            return bool(self.job_description)

    def analyze_relevance(self) -> Optional[Dict[str, Any]]:
        """Analyze resume relevance to job description using AI."""
        self._validate_inputs()
        prompt = self._get_analysis_prompt()
        analysis = self.ai_service.get_fix(prompt, {
            "resume": self.original_resume, 
            "job_description": self.job_description
        })
        
        if isinstance(analysis, str):
            try:
                import json
                return json.loads(analysis)
            except:
                # Create a structured response if parsing fails
                return {
                    "match_score": 70,
                    "matching_skills": [],
                    "missing_skills": [],
                    "improvement_suggestions": [analysis],
                    "keywords_to_add": []
                }
        return analysis

    def _validate_inputs(self) -> None:
        """Validate resume and job description exist"""
        if not self.original_resume or not self.job_description:
            raise ValueError("Resume and job description required")

    def _call_openai_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Make OpenAI API call with error handling"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None

    def optimize_resume(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Generate optimized resume using AI.
        
        Args:
            analysis (Dict[str, Any]): Analysis results from analyze_relevance()
            
        Returns:
            Optional[str]: Optimized resume content or None if failed
        """
        prompt = self._get_optimization_prompt(analysis)
        return self.ai_service.get_fix(prompt, {"analysis": analysis})

    def save_resume(self, optimized_content: str, output_format: str = 'docx') -> bool:
        """Save the optimized resume.
        
        Args:
            optimized_content (str): The optimized resume content
            output_format (str): Output format ('docx' or 'txt')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not optimized_content:
            logger.error("No content to save")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("optimized_resumes")
        output_dir.mkdir(exist_ok=True)
        
        try:
            if output_format == 'docx':
                doc = Document()
                doc = ResumeFormatter.format_docx(doc, optimized_content)
                filename = output_dir / f"optimized_resume_{timestamp}.docx"
                doc.save(filename)
            else:
                filename = output_dir / f"optimized_resume_{timestamp}.txt"
                with open(filename, 'w') as file:
                    file.write(optimized_content)
            
            logger.info(f"Optimized resume saved as: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving resume: {str(e)}")
            return False

    def _get_analysis_prompt(self) -> str:
        """Enhanced analysis prompt for better results."""
        return """Analyze the resume against the job description and provide a JSON response with this exact structure:
        {
            "match_score": <number between 0-100>,
            "matching_skills": ["skill1", "skill2", ...],
            "missing_skills": ["skill1", "skill2", ...],
            "improvement_suggestions": ["suggestion1", "suggestion2", ...],
            "keywords_to_add": ["keyword1", "keyword2", ...]
        }"""

    def _get_optimization_prompt(self, analysis: Dict[str, Any]) -> str:
        """Get optimization prompt with analysis context"""
        return f"""Based on the analysis results:
        - Match Score: {analysis.get('match_score', 0)}
        - Key Skills: {', '.join(analysis.get('matching_skills', []))}
        - Missing Skills: {', '.join(analysis.get('missing_skills', []))}
        
        Optimize this resume:
        {self.original_resume}
        
        For this job description:
        {self.job_description}
        """
        
    def process_job_url(self, url: str) -> bool:
        """Process job description from URL"""
        job_desc = self.job_scraper.extract_job_description(url)
        if not job_desc:
            logger.error("Failed to extract job description from URL")
            return False
            
        self.job_description = job_desc
        return True
        
    def get_advanced_analysis(self) -> Dict[str, Any]:
        """Get advanced resume analysis"""
        self._validate_inputs()
        
        analytics = ResumeAnalytics(self.original_resume, self.job_description)
        metrics = analytics.calculate_match_metrics()
        
        return {
            'basic_analysis': self.analyze_relevance(),
            'advanced_metrics': metrics
        }