import json
import re
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fuzzywuzzy import fuzz
import numpy as np
import asyncio

from app.config import settings


class EvaluationEngine:
    """AI-powered resume evaluation engine with hybrid scoring"""
    
    def __init__(self):
        """Initialize the evaluation engine"""
        self.embedding_model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self._initialize_models()
        
        # Scoring weights
        self.hard_match_weight = settings.hard_match_weight
        self.semantic_match_weight = settings.semantic_match_weight
        
        # Skill categories for better matching
        self.skill_categories = {
            'programming_languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 
                'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala'
            ],
            'web_technologies': [
                'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django',
                'Flask', 'Spring', 'ASP.NET', 'Laravel', 'HTML', 'CSS'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle',
                'SQL Server', 'SQLite', 'Elasticsearch'
            ],
            'cloud_devops': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
                'GitLab', 'GitHub', 'Terraform', 'Ansible'
            ],
            'data_science': [
                'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
                'Matplotlib', 'Jupyter', 'Apache Spark', 'Tableau'
            ]
        }
    
    def _initialize_models(self):
        """Initialize ML models"""
        try:
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            print("✓ Sentence transformer model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load sentence transformer model: {e}")
            self.embedding_model = None
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name for better matching"""
        skill = skill.strip().lower()
        
        # Handle common variations
        skill_mappings = {
            'js': 'javascript',
            'ts': 'typescript',
            'reactjs': 'react',
            'react.js': 'react',
            'nodejs': 'node.js',
            'node': 'node.js',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'aws': 'amazon web services',
            'gcp': 'google cloud platform'
        }
        
        return skill_mappings.get(skill, skill)
    
    def calculate_hard_match_score(
        self, 
        job_data: Dict[str, Any], 
        resume_data: Dict[str, Any]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate hard matching score based on exact skill matches"""
        
        # Get required and preferred skills from job
        required_skills = [self.normalize_skill(skill) for skill in job_data.get('required_skills', [])]
        preferred_skills = [self.normalize_skill(skill) for skill in job_data.get('preferred_skills', [])]
        all_job_skills = required_skills + preferred_skills
        
        # Get candidate skills
        candidate_skills = [self.normalize_skill(skill) for skill in resume_data.get('skills', [])]
        
        if not all_job_skills:
            return 0.0, [], []
        
        matched_skills = []
        
        # Exact matches
        for job_skill in all_job_skills:
            if job_skill in candidate_skills:
                matched_skills.append(job_skill)
        
        # Fuzzy matches for similar skills
        for job_skill in all_job_skills:
            if job_skill not in matched_skills:
                for candidate_skill in candidate_skills:
                    similarity = fuzz.ratio(job_skill, candidate_skill)
                    if similarity >= 85:  # 85% similarity threshold
                        matched_skills.append(job_skill)
                        break
        
        # Calculate score
        total_skills = len(all_job_skills)
        matched_count = len(matched_skills)
        
        # Weight required skills more heavily
        required_matched = sum(1 for skill in required_skills if skill in matched_skills)
        preferred_matched = sum(1 for skill in preferred_skills if skill in matched_skills)
        
        # Score calculation: required skills have 70% weight, preferred have 30%
        if len(required_skills) > 0:
            required_score = (required_matched / len(required_skills)) * 0.7
        else:
            required_score = 0
        
        if len(preferred_skills) > 0:
            preferred_score = (preferred_matched / len(preferred_skills)) * 0.3
        else:
            preferred_score = 0.3  # Full preferred score if no preferred skills listed
        
        hard_match_score = (required_score + preferred_score) * 100
        
        # Find missing skills
        missing_skills = [skill for skill in all_job_skills if skill not in matched_skills]
        
        return min(hard_match_score, 100.0), matched_skills, missing_skills
    
    def calculate_semantic_match_score(
        self, 
        job_data: Dict[str, Any], 
        resume_data: Dict[str, Any]
    ) -> float:
        """Calculate semantic matching score using embeddings"""
        
        if not self.embedding_model:
            # Fallback to TF-IDF based similarity
            return self._calculate_tfidf_similarity(job_data, resume_data)
        
        try:
            # Prepare job description
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}"
            job_text = job_text.strip()
            
            # Prepare resume text
            resume_text = resume_data.get('text', '')
            
            if not job_text or not resume_text:
                return 0.0
            
            # Generate embeddings
            job_embedding = self.embedding_model.encode([job_text])
            resume_embedding = self.embedding_model.encode([resume_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(job_embedding, resume_embedding)[0][0]
            
            # Convert to percentage
            semantic_score = float(similarity) * 100
            
            return min(semantic_score, 100.0)
        
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return self._calculate_tfidf_similarity(job_data, resume_data)
    
    def _calculate_tfidf_similarity(
        self, 
        job_data: Dict[str, Any], 
        resume_data: Dict[str, Any]
    ) -> float:
        """Fallback TF-IDF based similarity calculation"""
        try:
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}"
            resume_text = resume_data.get('text', '')
            
            if not job_text or not resume_text:
                return 0.0
            
            # Vectorize texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([job_text, resume_text])
            
            # Calculate similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity) * 100
        
        except Exception as e:
            print(f"Error in TF-IDF similarity: {e}")
            return 0.0
    
    def calculate_qualification_match(
        self, 
        job_data: Dict[str, Any], 
        resume_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Calculate qualification matching"""
        
        job_qualifications = job_data.get('qualifications', '').lower()
        resume_education = resume_data.get('education', [])
        
        matched_qualifications = []
        missing_qualifications = []
        
        # Common qualification keywords
        qualification_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree',
            'computer science', 'engineering', 'information technology',
            'mathematics', 'statistics'
        ]
        
        # Check education against job requirements
        resume_education_text = ' '.join([
            f"{edu.get('degree', '')} {edu.get('institution', '')}" 
            for edu in resume_education
        ]).lower()
        
        for keyword in qualification_keywords:
            if keyword in job_qualifications:
                if keyword in resume_education_text:
                    matched_qualifications.append(keyword)
                else:
                    missing_qualifications.append(keyword)
        
        return matched_qualifications, missing_qualifications
    
    def determine_suitability(self, relevance_score: float) -> str:
        """Determine suitability level based on score"""
        if relevance_score >= 80:
            return "High"
        elif relevance_score >= 60:
            return "Medium"
        else:
            return "Low"
    
    def generate_feedback(
        self, 
        relevance_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
        suitability: str
    ) -> str:
        """Generate personalized feedback for the candidate"""
        
        feedback_parts = []
        
        # Overall assessment
        if suitability == "High":
            feedback_parts.append("🎉 Excellent match! Your profile aligns very well with the job requirements.")
        elif suitability == "Medium":
            feedback_parts.append("👍 Good match! Your profile has strong potential for this role.")
        else:
            feedback_parts.append("💡 Your profile shows promise, but there are areas for improvement.")
        
        # Matched skills
        if matched_skills:
            matched_str = ", ".join(matched_skills[:5])  # Show top 5
            if len(matched_skills) > 5:
                matched_str += f" and {len(matched_skills) - 5} more"
            feedback_parts.append(f"✅ Strong skills match: {matched_str}")
        
        # Missing skills
        if missing_skills:
            missing_str = ", ".join(missing_skills[:3])  # Show top 3 missing
            feedback_parts.append(f"🎯 Consider developing: {missing_str}")
            
            if len(missing_skills) > 3:
                feedback_parts.append(f"📚 Additional skills to explore: {', '.join(missing_skills[3:6])}")
        
        # Recommendations based on score
        if relevance_score < 60:
            feedback_parts.append("💼 Recommendation: Focus on building the key skills mentioned above and gain relevant project experience.")
        elif relevance_score < 80:
            feedback_parts.append("🚀 Recommendation: You're on the right track! Consider specializing in a few key areas and showcasing relevant projects.")
        else:
            feedback_parts.append("⭐ Recommendation: Great profile! Consider applying and highlighting your strongest skills in your application.")
        
        return " ".join(feedback_parts)
    
    async def evaluate(
        self, 
        job_data: Dict[str, Any], 
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main evaluation method that combines hard and semantic matching
        """
        
        try:
            # Calculate hard match score
            hard_match_score, matched_skills, missing_skills = self.calculate_hard_match_score(
                job_data, resume_data
            )
            
            # Calculate semantic match score
            semantic_match_score = self.calculate_semantic_match_score(job_data, resume_data)
            
            # Calculate qualification matching
            matched_qualifications, missing_qualifications = self.calculate_qualification_match(
                job_data, resume_data
            )
            
            # Calculate final relevance score
            relevance_score = (
                hard_match_score * self.hard_match_weight +
                semantic_match_score * self.semantic_match_weight
            )
            
            # Determine suitability
            suitability = self.determine_suitability(relevance_score)
            
            # Generate feedback
            feedback = self.generate_feedback(
                relevance_score, matched_skills, missing_skills, suitability
            )
            
            return {
                'relevance_score': round(relevance_score, 2),
                'hard_match_score': round(hard_match_score, 2),
                'semantic_match_score': round(semantic_match_score, 2),
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'matched_qualifications': matched_qualifications,
                'missing_qualifications': missing_qualifications,
                'suitability': suitability,
                'feedback': feedback
            }
        
        except Exception as e:
            print(f"Error in evaluation: {e}")
            # Return a default evaluation result
            return {
                'relevance_score': 0.0,
                'hard_match_score': 0.0,
                'semantic_match_score': 0.0,
                'matched_skills': [],
                'missing_skills': job_data.get('required_skills', []),
                'matched_qualifications': [],
                'missing_qualifications': [],
                'suitability': 'Low',
                'feedback': f'Unable to complete evaluation due to technical error: {str(e)}'
            }