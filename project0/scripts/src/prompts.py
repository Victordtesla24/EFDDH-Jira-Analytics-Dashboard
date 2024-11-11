from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Prompts:
    """Container for all system prompts"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get base system prompt for AI interactions"""
        return (
            "You are an expert resume optimization assistant with deep knowledge of:\n"
            "- ATS systems and keyword optimization\n"
            "- Industry best practices for resume writing\n"
            "- Professional formatting and structure\n"
            "- Job market requirements and trends\n\n"
            "Provide specific, actionable advice while maintaining authenticity."
        )

    @staticmethod
    def format_analysis_prompt(resume: str, job_desc: str) -> str:
        """Format analysis prompt with inputs"""
        return (
            f"Analyze this resume against the job requirements:\n\n"
            f"RESUME:\n{resume}\n\n"
            f"JOB DESCRIPTION:\n{job_desc}\n\n"
            "Provide a detailed analysis in JSON format including:\n"
            "- Overall match score (0-100)\n"
            "- Matching skills and keywords\n"
            "- Missing required skills\n"
            "- Specific improvement suggestions\n"
            "- Industry-specific keywords to add"
        )

    @staticmethod
    def format_optimization_prompt(resume: str, job_description: str, analysis: Dict[str, Any]) -> str:
        """Format optimization prompt with inputs"""
        return (
            f"Optimize this resume for the job description:\n\n"
            f"RESUME:\n{resume}\n\n"
            f"JOB DESCRIPTION:\n{job_description}\n\n"
            f"ANALYSIS:\n{analysis}\n\n"
            "Provide a tailored resume in markdown format."
        )

# Removed redundant import and unused logger