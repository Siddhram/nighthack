#!/usr/bin/env python3
"""
Test the evaluation functionality end-to-end
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_evaluation_end_to_end():
    """Test the complete evaluation workflow"""
    print("🧪 Testing Complete Evaluation Workflow")
    print("=" * 50)
    
    # Step 1: Create a test job
    print("1️⃣ Creating test job...")
    job_data = {
        "title": "Frontend Developer",
        "company": "Test Company",
        "description": "Looking for a skilled frontend developer with React and JavaScript experience. Must have 2-3 years experience in web development.",
        "required_skills": ["React", "JavaScript", "HTML", "CSS"],
        "preferred_skills": ["TypeScript", "Node.js", "Git"],
        "qualifications": "Bachelor's degree in Computer Science",
        "experience_required": "2-3 years",
        "location": "Remote"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/", json=job_data)
        if response.status_code == 200:
            job_result = response.json()
            job_id = job_result['data']['id']
            print(f"✅ Job created with ID: {job_id}")
            print(f"   Required skills: {job_result['data']['required_skills']}")
            print(f"   Preferred skills: {job_result['data']['preferred_skills']}")
        else:
            print(f"❌ Failed to create job: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating job: {e}")
        return False
    
    # Step 2: Create a test resume
    print("\n2️⃣ Creating test resume...")
    resume_content = """John Doe
Frontend Developer
john.doe@email.com
+1-234-567-8900

SKILLS:
React, JavaScript, HTML, CSS, Git, Bootstrap

EXPERIENCE:
Frontend Developer at WebTech Solutions (2021-2023)
- Developed responsive web applications using React and JavaScript
- Collaborated with design teams to implement UI/UX designs
- Maintained and improved existing web applications

EDUCATION:
Bachelor of Science in Computer Science
Tech University (2017-2021)

PROJECTS:
E-commerce Website - Built using React, JavaScript, and CSS
Portfolio Website - Personal showcase of projects
"""
    
    try:
        files = {'file': ('test_resume.txt', resume_content, 'text/plain')}
        response = requests.post(f"{BASE_URL}/resumes/upload", files=files)
        if response.status_code == 200:
            resume_result = response.json()
            resume_id = resume_result['data']['id']
            print(f"✅ Resume uploaded with ID: {resume_id}")
            print(f"   Extracted skills: {resume_result['data']['skills']}")
            print(f"   Contact: {resume_result['data']['email']}")
        else:
            print(f"❌ Failed to upload resume: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading resume: {e}")
        return False
    
    # Step 3: Test evaluation
    print(f"\n3️⃣ Evaluating resume {resume_id} against job {job_id}...")
    try:
        response = requests.post(f"{BASE_URL}/evaluations/evaluate", params={
            'job_id': job_id,
            'resume_id': resume_id
        })
        
        if response.status_code == 200:
            eval_result = response.json()
            evaluation = eval_result['data']
            print("✅ Evaluation completed successfully!")
            print(f"   🎯 Relevance Score: {evaluation['relevance_score']}%")
            print(f"   🔍 Hard Match Score: {evaluation['hard_match_score']}%")
            print(f"   🧠 Semantic Match Score: {evaluation['semantic_match_score']}%")
            print(f"   ✅ Matched Skills ({len(evaluation['matched_skills'])}): {evaluation['matched_skills']}")
            print(f"   ❌ Missing Skills ({len(evaluation['missing_skills'])}): {evaluation['missing_skills']}")
            print(f"   📊 Suitability: {evaluation['suitability']}")
            print(f"   💬 Feedback: {evaluation['feedback'][:100]}...")
            return True
        else:
            print(f"❌ Failed to evaluate: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return False

def test_frontend_api():
    """Test the frontend API calls"""
    print("\n🌐 Testing Frontend API Integration")
    print("=" * 50)
    
    # Test jobs list
    try:
        response = requests.get(f"{BASE_URL}/jobs/")
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Jobs API working - Found {len(jobs['data'])} jobs")
        else:
            print(f"❌ Jobs API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Jobs API error: {e}")
    
    # Test resumes list
    try:
        response = requests.get(f"{BASE_URL}/resumes/")
        if response.status_code == 200:
            resumes = response.json()
            print(f"✅ Resumes API working - Found {len(resumes)} resumes")
        else:
            print(f"❌ Resumes API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Resumes API error: {e}")
    
    # Test evaluations list
    try:
        response = requests.get(f"{BASE_URL}/evaluations/")
        if response.status_code == 200:
            evaluations = response.json()
            print(f"✅ Evaluations API working - Found {len(evaluations['data'])} evaluations")
        else:
            print(f"❌ Evaluations API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Evaluations API error: {e}")

if __name__ == "__main__":
    print("🚀 Evaluation System Test Suite")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    # Test the complete workflow
    success = test_evaluation_end_to_end()
    
    # Test frontend integration
    test_frontend_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ The evaluation system is working correctly")
    else:
        print("❌ Some tests failed - check the backend server and API endpoints")