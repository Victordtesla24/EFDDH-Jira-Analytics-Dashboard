from typing import Dict, Any, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import logging

logger = logging.getLogger(__name__)

class ResumeAnalytics:
    """Advanced resume analytics"""
    
    def __init__(self, resume_text: str, job_description: str):
        self.resume = resume_text
        self.job_desc = job_description
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def calculate_match_metrics(self) -> Dict[str, Any]:
        """Calculate detailed match metrics"""
        return {
            'keyword_match_score': self._calculate_keyword_match(),
            'experience_relevance': self._analyze_experience_relevance(),
            'skills_coverage': self._analyze_skills_coverage(),
            'education_match': self._analyze_education_match(),
            'industry_alignment': self._analyze_industry_alignment(),
            'overall_match_probability': self._calculate_match_probability()
        }
        
    def _calculate_keyword_match(self) -> float:
        """Calculate keyword match score using TF-IDF"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([self.resume, self.job_desc])
            feature_names = self.vectorizer.get_feature_names_out()
            resume_vector = tfidf_matrix[0].toarray()[0]
            job_vector = tfidf_matrix[1].toarray()[0]
            
            matching_score = sum(1 for r, j in zip(resume_vector, job_vector) if r > 0 and j > 0)
            total_job_keywords = sum(1 for j in job_vector if j > 0)
            
            return matching_score / total_job_keywords if total_job_keywords > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Keyword matching failed: {str(e)}")
            return 0.0

    def _analyze_experience_relevance(self) -> Dict[str, Any]:
        """Analyze experience relevance using NLP"""
        resume_doc = self.nlp(self.resume)
        job_doc = self.nlp(self.job_desc)
        
        return {
            'relevance_score': resume_doc.similarity(job_doc),
            'key_phrases': self._extract_key_phrases(resume_doc)
        }

    def _analyze_skills_coverage(self) -> Dict[str, List[str]]:
        """Analyze skills coverage"""
        job_skills = self._extract_skills(self.job_desc)
        resume_skills = self._extract_skills(self.resume)
        
        return {
            'matching_skills': list(job_skills & resume_skills),
            'missing_skills': list(job_skills - resume_skills)
        }
        
    def _extract_skills(self, text: str) -> Set[str]:
        """Extract skills from text using NLP"""
        doc = self.nlp(text)
        return {token.text.lower() for token in doc 
                if token.pos_ in {'NOUN', 'PROPN'} 
                and len(token.text) > 2}

    def _extract_key_phrases(self, doc: spacy.tokens.Doc) -> List[str]:
        """Extract key phrases from spaCy doc"""
        return [chunk.text for chunk in doc.noun_chunks 
                if len(chunk.text.split()) > 1]

    def _analyze_education_match(self) -> Dict[str, Any]:
        """Analyze education requirements match"""
        edu_keywords = {'degree', 'bachelor', 'master', 'phd', 'diploma'}
        job_doc = self.nlp(self.job_desc.lower())
        resume_doc = self.nlp(self.resume.lower())
        
        job_edu = {token.text for token in job_doc if token.text in edu_keywords}
        resume_edu = {token.text for token in resume_doc if token.text in edu_keywords}
        
        return {
            'required_education': list(job_edu),
            'candidate_education': list(resume_edu),
            'education_match': len(job_edu & resume_edu) / len(job_edu) if job_edu else 1.0
        }
        
    def _analyze_industry_alignment(self) -> float:
        """Analyze industry alignment score"""
        job_doc = self.nlp(self.job_desc)
        resume_doc = self.nlp(self.resume)
        return job_doc.similarity(resume_doc)
        
    def _calculate_match_probability(self) -> float:
        """Calculate overall match probability"""
        keyword_weight = 0.4
        exp_weight = 0.3
        edu_weight = 0.2
        industry_weight = 0.1
        
        keyword_score = self._calculate_keyword_match()
        exp_score = self._analyze_experience_relevance()['relevance_score']
        edu_score = self._analyze_education_match()['education_match']
        industry_score = self._analyze_industry_alignment()
        
        return (keyword_score * keyword_weight +
                exp_score * exp_weight +
                edu_score * edu_weight +
                industry_score * industry_weight)