import unittest
from resume_optimiser import optimize_resume, ResumeOptimizer
from auto_error_handler import (
    AutoErrorHandler,
    PackageManager,
    AIService,
    FixProcessor
)
from auto_error_handler.exceptions import (
    FixApplicationError,
    ValidationError,
    AIServiceError
)
from unittest.mock import patch, MagicMock

class TestResumeOptimizer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.sample_resume = "Software engineer with 5 years experience"
        self.sample_job = "Looking for senior software engineer"
        self.api_key = "test-api-key"
        self.optimizer = ResumeOptimizer(self.api_key)
        self.error_handler = AutoErrorHandler(self.api_key)
        
    def test_optimize_resume_basic(self):
        """Test basic resume optimization functionality"""
        input_resume = "Sample resume content"
        input_job = "Sample job description"
        
        result = optimize_resume(input_resume, input_job)
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['score'], float)
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreaterEqual(result['score'], 0.0)
        self.assertLessEqual(result['score'], 1.0)

    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        handler = AutoErrorHandler(self.api_key)
        self.assertIsNotNone(handler)
        self.assertEqual(handler.api_key, self.api_key)
        self.assertEqual(handler.max_retries, 3)

    @patch('openai.ChatCompletion.create')
    def test_error_handler_ai_fix(self, mock_openai):
        """Test AI-based error fixing"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"type": "code_fix", "file": "test.py", "changes": [{"line": 1, "code": "import requests"}]}'
        mock_openai.return_value = mock_response
        
        error = ImportError("No module named 'requests'")
        context = {
            "file": "test.py",
            "function": "test_func",
            "variables": {"local_var": "value"}
        }
        
        result = self.error_handler.handle_error(error, context)
        self.assertTrue(result)

    @patch('resume_optimiser.ResumeOptimizer._call_openai_api')
    def test_analyze_relevance(self, mock_api):
        """Test resume analysis with mocked API"""
        mock_api.return_value = {
            "match_score": 85,
            "matching_skills": ["python", "testing"],
            "missing_skills": ["docker"]
        }
        
        optimizer = ResumeOptimizer("test-key")
        optimizer.original_resume = self.sample_resume
        optimizer.job_description = self.sample_job
        
        result = optimizer.analyze_relevance()
        self.assertIsNotNone(result)
        self.assertIn("match_score", result)
        
    def test_get_advanced_analysis(self):
        """Test advanced analysis integration"""
        optimizer = ResumeOptimizer("test-key")
        optimizer.original_resume = self.sample_resume
        optimizer.job_description = self.sample_job
        
        with patch('resume_analytics.ResumeAnalytics.calculate_match_metrics') as mock_metrics:
            mock_metrics.return_value = {"keyword_match_score": 0.8}
            result = optimizer.get_advanced_analysis()
            
        self.assertIsInstance(result, dict)
        self.assertIn('advanced_metrics', result)

    def test_optimize_resume_error(self):
        """Test error handling for empty inputs"""
        with self.assertRaises(ValueError):
            optimize_resume("", "")
            
        with self.assertRaises(ValueError):
            optimize_resume("some resume", "")
            
        with self.assertRaises(ValueError):
            optimize_resume("", "some job")
        
    def test_resume_optimizer_class(self):
        """Test ResumeOptimizer class initialization"""
        optimizer = ResumeOptimizer("fake-api-key")
        self.assertIsNotNone(optimizer)
        
        with self.assertRaises(ValueError):
            ResumeOptimizer("")  # Empty API key should raise error

    def test_resume_analytics(self):
        """Test resume analytics functionality"""
        from resume_optimiser import ResumeAnalytics
        
        analytics = ResumeAnalytics(self.sample_resume, self.sample_job)
        metrics = analytics.calculate_match_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('keyword_match_score', metrics)
        self.assertIn('skills_coverage', metrics)
        
    def test_ai_resume_writer(self):
        """Test AI resume writer functionality"""
        from resume_optimiser import AIResumeWriter
        
        writer = AIResumeWriter(self.api_key)
        metrics = {'match_score': 0.8}
        
        with patch('openai.ChatCompletion.create') as mock_openai:
            mock_openai.return_value.choices[0].message.content = "Tailored resume"
            result = writer.tailor_resume(self.sample_resume, self.sample_job, metrics)
            self.assertIsInstance(result, str)
            
    def test_resume_formatter(self):
        """Test resume formatter functionality"""
        from resume_optimiser import ResumeFormatter
        from docx import Document
        
        doc = Document()
        content = "Test Resume\n\nEXPERIENCE\nSoftware Engineer"
        
        formatted_doc = ResumeFormatter.format_docx(doc, content)
        self.assertIsInstance(formatted_doc, Document)

    def test_error_handler_components(self):
        """Test error handler component initialization"""
        handler = AutoErrorHandler(self.api_key)
        
        self.assertIsInstance(handler.package_manager, PackageManager)
        self.assertIsInstance(handler.ai_service, AIService)
        self.assertIsInstance(handler.fix_processor, FixProcessor)
        
    def test_error_handler_exceptions(self):
        """Test custom exception handling"""
        handler = AutoErrorHandler(self.api_key)
        
        with self.assertRaises(ValidationError):
            handler.fix_processor._validate_fix({})
            
        with self.assertRaises(AIServiceError):
            handler.ai_service.get_fix(Exception(), {})

if __name__ == '__main__':
    unittest.main()