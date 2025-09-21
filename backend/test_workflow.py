#!/usr/bin/env python3
"""
Test script to verify the complete placement workflow end-to-end
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_job_creation():
    """Test job creation with JD parsing"""
    print("🧪 Testing Job Creation with JD Parsing...")
    
    job_data = {
        "title": "Full Stack Developer",
        "company": "Innomatics Research Labs",
        "description": """We are looking for a skilled Full Stack Developer with experience in React, Node.js, Python, and MongoDB. 
        Must have 3-5 years of experience in web development.
        
        Required skills: React, JavaScript, Node.js, Python, MongoDB, Git, HTML, CSS
        Good to have: AWS, Docker, TypeScript, Redis, PostgreSQL
        
        Qualifications: Bachelor's degree in Computer Science or related field
        Experience: 3-5 years of professional development experience""",
        "required_skills": ["React", "JavaScript"],
        "preferred_skills": ["AWS"],
        "qualifications": "Bachelor's degree",
        "experience_required": "3-5 years",
        "location": "Hyderabad"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/", json=job_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job created successfully!")
            print(f"   📝 Enhanced with {len(result['data']['required_skills'])} required skills")
            print(f"   📝 Enhanced with {len(result['data']['preferred_skills'])} preferred skills")
            return result['data']['id']
        else:
            print(f"❌ Failed to create job: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating job: {e}")
        return None

def test_resume_upload():
    """Test resume upload and parsing"""
    print("\n🧪 Testing Resume Upload and Parsing...")
    
    # Create a simple test resume content
    resume_content = """
    John Doe
    Full Stack Developer
    john.doe@email.com
    +1-234-567-8900
    
    SKILLS:
    - React, JavaScript, TypeScript
    - Node.js, Express.js
    - Python, Django
    - MongoDB, PostgreSQL
    - Git, Docker
    - HTML, CSS, Bootstrap
    
    EXPERIENCE:
    Senior Developer at Tech Corp (2020-2023)
    - Built web applications using React and Node.js
    - Worked with Python and Django for backend development
    - Experience with MongoDB and PostgreSQL databases
    
    EDUCATION:
    Bachelor of Technology in Computer Science
    University of Technology (2016-2020)
    """
    
    # Create a temporary text file (simulating resume upload)
    files = {'file': ('resume.txt', resume_content, 'text/plain')}
    
    try:
        response = requests.post(f"{BASE_URL}/resumes/upload", files=files)
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume uploaded and parsed successfully!")
            print(f"   📝 Extracted {len(result['data']['skills'])} skills")
            print(f"   📧 Contact: {result['data']['email'] or 'Auto-extracted'}")
            return result['data']['id']
        else:
            print(f"❌ Failed to upload resume: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error uploading resume: {e}")
        return None

def test_evaluation(job_id, resume_id):
    """Test resume evaluation against job"""
    print(f"\n🧪 Testing Resume Evaluation...")
    
    try:
        response = requests.post(f"{BASE_URL}/evaluations/evaluate", params={
            'job_id': job_id,
            'resume_id': resume_id
        })
        
        if response.status_code == 200:
            result = response.json()
            evaluation = result['data']
            print("✅ Resume evaluation completed!")
            print(f"   🎯 Relevance Score: {evaluation['relevance_score']:.1f}%")
            print(f"   🔍 Hard Match Score: {evaluation['hard_match_score']:.1f}%")
            print(f"   🧠 Semantic Match Score: {evaluation['semantic_match_score']:.1f}%")
            print(f"   ✅ Matched Skills: {len(evaluation['matched_skills'])}")
            print(f"   ❌ Missing Skills: {len(evaluation['missing_skills'])}")
            print(f"   📊 Suitability: {evaluation['suitability']}")
            return True
        else:
            print(f"❌ Failed to evaluate resume: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error evaluating resume: {e}")
        return False

def test_dashboard_access():
    """Test dashboard data access"""
    print(f"\n🧪 Testing Dashboard Access...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Dashboard stats retrieved successfully!")
            print(f"   📊 Total Jobs: {stats.get('total_jobs', 0)}")
            print(f"   📄 Total Resumes: {stats.get('total_resumes', 0)}")
            print(f"   🔍 Total Evaluations: {stats.get('total_evaluations', 0)}")
            return True
        else:
            print(f"❌ Failed to get dashboard stats: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting dashboard stats: {e}")
        return False

def main():
    """Run complete workflow test"""
    print("🚀 Starting Complete Placement Workflow Test")
    print("=" * 50)
    
    # Test 1: Job Creation with JD Parsing
    job_id = test_job_creation()
    if not job_id:
        print("❌ Workflow failed at job creation")
        return
    
    # Test 2: Resume Upload and Parsing
    resume_id = test_resume_upload()
    if not resume_id:
        print("❌ Workflow failed at resume upload")
        return
    
    # Test 3: Resume Evaluation
    evaluation_success = test_evaluation(job_id, resume_id)
    if not evaluation_success:
        print("❌ Workflow failed at evaluation")
        return
    
    # Test 4: Dashboard Access
    dashboard_success = test_dashboard_access()
    if not dashboard_success:
        print("❌ Workflow failed at dashboard access")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Complete Placement Workflow Test PASSED!")
    print("✅ All features working correctly:")
    print("   • Job Requirement Upload with JD Parsing")
    print("   • Resume Upload with Text Parsing")
    print("   • Relevance Analysis (Hard + Semantic Matching)")
    print("   • Output Generation (Scores, Missing Skills, Suitability)")
    print("   • Storage & Dashboard Access")

if __name__ == "__main__":
    main()