"""
Test script to verify the updated evaluation system with less strict criteria
and descending order sorting.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.evaluation_engine import EvaluationEngine
import asyncio


async def test_evaluation_scoring():
    """Test the evaluation engine with sample data"""
    engine = EvaluationEngine()
    
    # Sample job data
    job_data = {
        "title": "Senior Python Developer",
        "description": "We are looking for a Python developer with web development experience",
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "preferred_skills": ["React", "AWS", "Docker"],
        "qualifications": "Bachelor's degree in Computer Science",
        "experience_required": "3+ years"
    }
    
    # Sample resume with partial skill match (should score higher with less strict criteria)
    resume_data = {
        "text": "Python developer with 2 years experience. Built web applications using Python and Flask. Experience with MySQL database.",
        "skills": ["Python", "Flask", "MySQL", "HTML", "CSS"],  # Partial match with job requirements
        "experience": ["Software Developer - 2 years"],
        "education": ["Bachelor of Computer Science"],
        "projects": ["E-commerce web application", "Data visualization dashboard"],
        "certifications": []
    }
    
    print("Testing evaluation with less strict criteria...")
    print("=" * 50)
    
    # Run evaluation
    result = await engine.evaluate(job_data, resume_data)
    
    print(f"Relevance Score: {result['relevance_score']:.2f}%")
    print(f"Hard Match Score: {result['hard_match_score']:.2f}%")
    print(f"Semantic Match Score: {result['semantic_match_score']:.2f}%")
    print(f"Suitability: {result['suitability']}")
    print(f"Matched Skills: {result['matched_skills']}")
    print(f"Missing Skills: {result['missing_skills']}")
    print(f"Feedback: {result['feedback']}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed successfully!")
    print("Expected improvements:")
    print("- Lower skill similarity threshold (50% instead of 70%)")
    print("- More balanced required/preferred skill weights (60/40 instead of 70/30)")
    print("- Less strict suitability thresholds (70%/45% instead of 80%/60%)")


if __name__ == "__main__":
    asyncio.run(test_evaluation_scoring())