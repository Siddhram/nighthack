import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fuzzywuzzy import fuzz, process
import re
from dataclasses import dataclass

from .jd_parser import JobDescriptionAnalysis
from .innomatics_resume_analyzer import ResumeAnalysis
from ..models.innomatics_schemas import HardMatchResult, SoftMatchResult, RelevanceAnalysisResult, FitVerdict


@dataclass
class WeightingConfig:
    """Configuration for scoring weights in Innomatics system"""
    hard_match_weight: float = 0.6  # 60% for hard matching
    soft_match_weight: float = 0.4  # 40% for semantic matching
    
    # Hard match sub-weights (should sum to 1.0)
    must_have_skills_weight: float = 0.4  # 40% of hard match
    good_to_have_skills_weight: float = 0.2  # 20% of hard match
    qualification_weight: float = 0.2  # 20% of hard match
    experience_weight: float = 0.2  # 20% of hard match
    
    # Soft match sub-weights (should sum to 1.0)
    semantic_similarity_weight: float = 0.5  # 50% of soft match
    role_alignment_weight: float = 0.3  # 30% of soft match
    project_relevance_weight: float = 0.2  # 20% of soft match
    
    # Fit verdict thresholds
    high_fit_threshold: float = 75.0  # >= 75 is High fit
    medium_fit_threshold: float = 50.0  # >= 50 is Medium fit
    # < 50 is Low fit


class InnomaticsHybridScoringEngine:
    """
    Advanced Hybrid Scoring Engine for Innomatics Research Labs
    
    Combines:
    1. Hard Matching (60%): Exact keyword/skill matching with fuzzy logic
    2. Soft Matching (40%): Semantic similarity using embeddings and NLP
    
    Generates:
    - Relevance Score (0-100)
    - Fit Verdict (High/Medium/Low)  
    - Missing Elements Analysis
    - Personalized Improvement Suggestions
    """
    
    def __init__(self, config: WeightingConfig = None):
        """Initialize the hybrid scoring engine"""
        self.config = config or WeightingConfig()
        
        # Initialize sentence transformer for semantic matching
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Sentence transformer model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.sentence_model = None
        
        # Initialize TF-IDF vectorizer for keyword matching
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Fuzzy matching threshold
        self.fuzzy_threshold = 80  # Minimum similarity score for fuzzy matching

    def evaluate_resume_relevance(
        self, 
        job_analysis: JobDescriptionAnalysis, 
        resume_analysis: ResumeAnalysis
    ) -> RelevanceAnalysisResult:
        """
        Comprehensive evaluation of resume relevance to job description
        
        Args:
            job_analysis: Parsed job description analysis
            resume_analysis: Parsed resume analysis
            
        Returns:
            RelevanceAnalysisResult: Complete evaluation with scores and feedback
        """
        # Step 1: Hard Matching (Exact + Fuzzy keyword matching)
        hard_match_result = self._perform_hard_matching(job_analysis, resume_analysis)
        
        # Step 2: Soft Matching (Semantic similarity)
        soft_match_result = self._perform_soft_matching(job_analysis, resume_analysis)
        
        # Step 3: Calculate final relevance score
        relevance_score = self._calculate_relevance_score(hard_match_result, soft_match_result)
        
        # Step 4: Determine fit verdict
        fit_verdict = self._determine_fit_verdict(relevance_score)
        
        # Step 5: Identify missing elements and generate suggestions
        missing_elements = self._identify_missing_elements(job_analysis, resume_analysis, hard_match_result)
        improvement_suggestions = self._generate_improvement_suggestions(
            job_analysis, resume_analysis, hard_match_result, soft_match_result
        )
        
        return RelevanceAnalysisResult(
            hard_match=hard_match_result,
            soft_match=soft_match_result,
            relevance_score=relevance_score,
            fit_verdict=fit_verdict,
            missing_elements=missing_elements,
            improvement_suggestions=improvement_suggestions
        )

    def _perform_hard_matching(
        self, 
        job_analysis: JobDescriptionAnalysis, 
        resume_analysis: ResumeAnalysis
    ) -> HardMatchResult:
        """
        Perform hard matching using exact and fuzzy string matching
        
        Hard matching includes:
        1. Must-have skills matching (critical)
        2. Good-to-have skills matching (preferred)
        3. Qualification matching
        4. Experience level matching
        """
        
        # 1. Must-have skills matching
        matched_must_have, missing_must_have = self._match_skills(
            job_analysis.must_have_skills,
            resume_analysis.extracted_skills + resume_analysis.technical_skills
        )
        
        # 2. Good-to-have skills matching
        matched_good_to_have, missing_good_to_have = self._match_skills(
            job_analysis.good_to_have_skills,
            resume_analysis.extracted_skills + resume_analysis.technical_skills
        )
        
        # 3. Qualification matching
        qualification_match = self._match_qualifications(
            job_analysis.qualifications,
            resume_analysis.education
        )
        
        # 4. Experience matching
        experience_match = self._match_experience(
            job_analysis.experience_required,
            resume_analysis.total_experience_years,
            resume_analysis.work_experience
        )
        
        # Calculate hard match score (out of 50 points, since it's 60% of total)
        hard_match_score = self._calculate_hard_match_score(
            matched_must_have, job_analysis.must_have_skills,
            matched_good_to_have, job_analysis.good_to_have_skills,
            qualification_match, experience_match
        )
        
        return HardMatchResult(
            matched_must_have_skills=matched_must_have,
            matched_good_to_have_skills=matched_good_to_have,
            missing_must_have_skills=missing_must_have,
            missing_good_to_have_skills=missing_good_to_have,
            qualification_match=qualification_match,
            experience_match=experience_match,
            hard_match_score=hard_match_score
        )

    def _perform_soft_matching(
        self,
        job_analysis: JobDescriptionAnalysis,
        resume_analysis: ResumeAnalysis
    ) -> SoftMatchResult:
        """
        Perform soft matching using semantic similarity and NLP
        
        Soft matching includes:
        1. Overall semantic similarity (JD vs Resume text)
        2. Role alignment (job responsibilities vs candidate experience)
        3. Project relevance (projects vs job requirements)
        """
        
        # 1. Semantic similarity between JD and Resume
        semantic_score = self._calculate_semantic_similarity(
            job_analysis.job_description,
            resume_analysis.parsed_text
        )
        
        # 2. Role alignment score
        role_alignment_score = self._calculate_role_alignment(
            job_analysis.role_responsibilities,
            resume_analysis.work_experience
        )
        
        # 3. Project relevance score
        project_relevance_score = self._calculate_project_relevance(
            job_analysis.technical_skills + job_analysis.domain_keywords,
            resume_analysis.projects
        )
        
        # Calculate overall semantic score (out of 40 points)
        overall_semantic_score = (
            semantic_score * self.config.semantic_similarity_weight +
            role_alignment_score * self.config.role_alignment_weight +
            project_relevance_score * self.config.project_relevance_weight
        ) * 40  # Scale to 40 points (40% of total)
        
        return SoftMatchResult(
            semantic_similarity_score=semantic_score * 40,
            role_alignment_score=role_alignment_score * 40,
            project_relevance_score=project_relevance_score * 40,
            overall_semantic_score=overall_semantic_score
        )

    def _match_skills(self, required_skills: List[str], candidate_skills: List[str]) -> Tuple[List[str], List[str]]:
        """Match required skills with candidate skills using exact and fuzzy matching"""
        matched_skills = []
        missing_skills = []
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        
        for required_skill in required_skills:
            required_skill_lower = required_skill.lower()
            
            # Exact match first
            if required_skill_lower in candidate_skills_lower:
                matched_skills.append(required_skill)
                continue
            
            # Fuzzy match for similar skills
            best_match = process.extractOne(
                required_skill_lower, 
                candidate_skills_lower,
                scorer=fuzz.token_set_ratio
            )
            
            if best_match and best_match[1] >= self.fuzzy_threshold:
                matched_skills.append(required_skill)
            else:
                missing_skills.append(required_skill)
        
        return matched_skills, missing_skills

    def _match_qualifications(self, required_qualifications: List[str], candidate_education: List[Dict]) -> bool:
        """Check if candidate meets qualification requirements"""
        if not required_qualifications:
            return True
        
        candidate_degrees = []
        for edu in candidate_education:
            candidate_degrees.append(edu.get('degree', '').lower())
            candidate_degrees.append(edu.get('field', '').lower())
        
        candidate_text = ' '.join(candidate_degrees)
        
        for required_qual in required_qualifications:
            required_qual_lower = required_qual.lower()
            
            # Check for degree level matches
            if any(keyword in candidate_text for keyword in ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'bca', 'mca']):
                if any(field in candidate_text for field in ['computer', 'information', 'technology', 'engineering']):
                    return True
        
        return len(candidate_education) > 0  # At least has some education

    def _match_experience(self, required_experience: str, candidate_years: float, work_experience: List[Dict]) -> bool:
        """Check if candidate meets experience requirements"""
        # Extract years from required experience
        years_match = re.search(r'(\d+)', required_experience)
        if not years_match:
            return True  # No specific requirement
        
        required_years = int(years_match.group(1))
        
        # For fresh graduate roles (0-1 years)
        if required_years <= 1:
            return candidate_years >= 0
        
        # For experienced roles, allow some flexibility
        return candidate_years >= (required_years * 0.8)  # 80% of required experience

    def _calculate_hard_match_score(
        self,
        matched_must_have: List[str],
        total_must_have: List[str], 
        matched_good_to_have: List[str],
        total_good_to_have: List[str],
        qualification_match: bool,
        experience_match: bool
    ) -> float:
        """Calculate hard match score using weighted formula"""
        
        # Must-have skills score (40% of hard match)
        must_have_score = (len(matched_must_have) / max(len(total_must_have), 1)) * self.config.must_have_skills_weight
        
        # Good-to-have skills score (20% of hard match)
        good_to_have_score = (len(matched_good_to_have) / max(len(total_good_to_have), 1)) * self.config.good_to_have_skills_weight
        
        # Qualification score (20% of hard match)
        qualification_score = (1.0 if qualification_match else 0.0) * self.config.qualification_weight
        
        # Experience score (20% of hard match)
        experience_score = (1.0 if experience_match else 0.0) * self.config.experience_weight
        
        # Total hard match score (out of 60 points, since hard match is 60% of total)
        total_score = (must_have_score + good_to_have_score + qualification_score + experience_score) * 60
        
        return min(total_score, 60.0)

    def _calculate_semantic_similarity(self, job_description: str, resume_text: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        if not self.sentence_model:
            # Fallback to TF-IDF similarity
            return self._calculate_tfidf_similarity(job_description, resume_text)
        
        try:
            # Get embeddings for both texts
            job_embedding = self.sentence_model.encode([job_description])
            resume_embedding = self.sentence_model.encode([resume_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(job_embedding, resume_embedding)[0][0]
            
            return max(0.0, similarity)  # Ensure non-negative
            
        except Exception as e:
            print(f"Error in semantic similarity calculation: {e}")
            return self._calculate_tfidf_similarity(job_description, resume_text)

    def _calculate_tfidf_similarity(self, job_description: str, resume_text: str) -> float:
        """Fallback TF-IDF similarity calculation"""
        try:
            # Fit TF-IDF on both documents
            tfidf_matrix = self.tfidf.fit_transform([job_description, resume_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return max(0.0, similarity)
            
        except Exception as e:
            print(f"Error in TF-IDF similarity: {e}")
            return 0.0

    def _calculate_role_alignment(self, job_responsibilities: List[str], work_experience: List[Dict]) -> float:
        """Calculate how well candidate's experience aligns with job responsibilities"""
        if not job_responsibilities or not work_experience:
            return 0.0
        
        # Extract experience descriptions
        experience_text = ' '.join([
            exp.get('role', '') + ' ' + str(exp.get('duration', ''))
            for exp in work_experience
        ])
        
        responsibilities_text = ' '.join(job_responsibilities)
        
        # Use semantic similarity for role alignment
        return self._calculate_semantic_similarity(responsibilities_text, experience_text)

    def _calculate_project_relevance(self, job_keywords: List[str], candidate_projects: List[Dict]) -> float:
        """Calculate relevance of candidate projects to job requirements"""
        if not candidate_projects:
            return 0.0
        
        # Extract project descriptions and technologies
        project_text = ' '.join([
            proj.get('title', '') + ' ' + proj.get('description', '') + ' ' + 
            ' '.join(proj.get('technologies', []))
            for proj in candidate_projects
        ])
        
        job_keywords_text = ' '.join(job_keywords)
        
        # Calculate similarity between project content and job requirements
        return self._calculate_semantic_similarity(job_keywords_text, project_text)

    def _calculate_relevance_score(self, hard_match: HardMatchResult, soft_match: SoftMatchResult) -> float:
        """Calculate final relevance score (0-100) using weighted combination"""
        
        # Weighted combination of hard and soft match scores
        relevance_score = (
            hard_match.hard_match_score * self.config.hard_match_weight +
            soft_match.overall_semantic_score * self.config.soft_match_weight
        )
        
        return min(100.0, max(0.0, relevance_score))

    def _determine_fit_verdict(self, relevance_score: float) -> FitVerdict:
        """Determine fit verdict based on relevance score"""
        if relevance_score >= self.config.high_fit_threshold:
            return FitVerdict.HIGH
        elif relevance_score >= self.config.medium_fit_threshold:
            return FitVerdict.MEDIUM
        else:
            return FitVerdict.LOW

    def _identify_missing_elements(
        self,
        job_analysis: JobDescriptionAnalysis,
        resume_analysis: ResumeAnalysis,
        hard_match: HardMatchResult
    ) -> List[str]:
        """Identify missing elements that could improve candidate fit"""
        missing_elements = []
        
        # Add missing must-have skills (critical)
        for skill in hard_match.missing_must_have_skills:
            missing_elements.append(f"Critical skill: {skill}")
        
        # Add missing good-to-have skills (if significant gap)
        if len(hard_match.missing_good_to_have_skills) > len(hard_match.matched_good_to_have_skills):
            for skill in hard_match.missing_good_to_have_skills[:3]:  # Top 3
                missing_elements.append(f"Preferred skill: {skill}")
        
        # Check for missing certifications
        if not hard_match.qualification_match:
            missing_elements.append("Relevant technical certifications")
        
        # Check for project gaps
        if len(resume_analysis.projects) < 2:
            missing_elements.append("More relevant projects demonstrating technical skills")
        
        # Check for experience gaps
        if not hard_match.experience_match:
            missing_elements.append(f"Additional experience in {job_analysis.role_title}")
        
        return missing_elements

    def _generate_improvement_suggestions(
        self,
        job_analysis: JobDescriptionAnalysis,
        resume_analysis: ResumeAnalysis,
        hard_match: HardMatchResult,
        soft_match: SoftMatchResult
    ) -> List[str]:
        """Generate personalized improvement suggestions for the candidate"""
        suggestions = []
        
        # Skill-based suggestions
        if hard_match.missing_must_have_skills:
            suggestions.append(
                f"🎯 Priority: Learn {', '.join(hard_match.missing_must_have_skills[:3])} "
                f"as these are critical for the {job_analysis.role_title} role"
            )
        
        if len(hard_match.matched_must_have_skills) > 0 and hard_match.missing_must_have_skills:
            suggestions.append(
                f"💡 You have {len(hard_match.matched_must_have_skills)} out of "
                f"{len(job_analysis.must_have_skills)} required skills. Focus on the missing ones."
            )
        
        # Project suggestions
        if len(resume_analysis.projects) < 2:
            suggestions.append(
                f"🚀 Build 2-3 projects using {', '.join(job_analysis.technical_skills[:3])} "
                f"to demonstrate practical skills"
            )
        
        # Experience suggestions
        if resume_analysis.total_experience_years < 1 and "senior" not in job_analysis.role_title.lower():
            suggestions.append(
                "📈 Consider internships or freelance projects to gain relevant experience"
            )
        
        # Certification suggestions
        if not hard_match.qualification_match:
            relevant_certs = [cert for cert in job_analysis.qualifications if 'certified' in cert.lower()]
            if relevant_certs:
                suggestions.append(
                    f"🏆 Consider getting certified in {relevant_certs[0]} to strengthen your profile"
                )
        
        # Soft skills suggestions based on role
        if soft_match.role_alignment_score < 30:
            suggestions.append(
                "💬 Highlight your experience with teamwork, communication, and problem-solving skills"
            )
        
        # Resume optimization
        if resume_analysis.resume_quality_score < 7:
            suggestions.append(
                "📝 Improve resume structure: add quantified achievements, technical project details, and contact links"
            )
        
        return suggestions[:5]  # Limit to top 5 suggestions

    def get_detailed_analysis_report(
        self,
        job_analysis: JobDescriptionAnalysis,
        resume_analysis: ResumeAnalysis,
        result: RelevanceAnalysisResult
    ) -> Dict[str, any]:
        """Generate a detailed analysis report for placement team review"""
        return {
            "candidate_summary": {
                "name": resume_analysis.student_name,
                "experience_years": resume_analysis.total_experience_years,
                "education": resume_analysis.education[0]['degree'] if resume_analysis.education else 'Not specified',
                "top_skills": resume_analysis.technical_skills[:5],
                "resume_quality": resume_analysis.resume_quality_score
            },
            "job_summary": {
                "role": job_analysis.role_title,
                "company": job_analysis.company_name,
                "required_skills": len(job_analysis.must_have_skills),
                "experience_required": job_analysis.experience_required
            },
            "scoring_breakdown": {
                "hard_match_score": result.hard_match.hard_match_score,
                "soft_match_score": result.soft_match.overall_semantic_score,
                "final_score": result.relevance_score,
                "fit_verdict": result.fit_verdict
            },
            "match_details": {
                "matched_must_have": len(result.hard_match.matched_must_have_skills),
                "total_must_have": len(job_analysis.must_have_skills),
                "matched_good_to_have": len(result.hard_match.matched_good_to_have_skills),
                "qualification_match": result.hard_match.qualification_match,
                "experience_match": result.hard_match.experience_match
            },
            "recommendations": {
                "missing_elements": result.missing_elements,
                "improvement_suggestions": result.improvement_suggestions,
                "interview_focus": self._generate_interview_focus_areas(job_analysis, resume_analysis, result)
            }
        }

    def _generate_interview_focus_areas(
        self,
        job_analysis: JobDescriptionAnalysis,
        resume_analysis: ResumeAnalysis,
        result: RelevanceAnalysisResult
    ) -> List[str]:
        """Generate focus areas for interview based on analysis"""
        focus_areas = []
        
        # Focus on matched skills for deeper assessment
        if result.hard_match.matched_must_have_skills:
            focus_areas.append(f"Deep dive into {', '.join(result.hard_match.matched_must_have_skills[:2])}")
        
        # Focus on projects if available
        if resume_analysis.projects:
            focus_areas.append(f"Technical discussion about {resume_analysis.projects[0]['title']}")
        
        # Focus on missing skills assessment
        if result.hard_match.missing_must_have_skills:
            focus_areas.append(f"Assess learning ability and interest in {result.hard_match.missing_must_have_skills[0]}")
        
        return focus_areas[:3]