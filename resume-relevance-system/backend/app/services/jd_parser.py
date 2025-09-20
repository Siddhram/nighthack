import re
import spacy
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class JobDescriptionAnalysis:
    """Structured analysis of job description for Innomatics Research Labs"""
    role_title: str
    company_name: str
    must_have_skills: List[str]  # Critical/mandatory skills
    good_to_have_skills: List[str]  # Preferred/nice-to-have skills
    qualifications: List[str]  # Education, certifications
    experience_required: str  # e.g., "2-5 years"
    role_responsibilities: List[str]  # Key job duties
    technical_skills: List[str]  # Programming languages, tools
    soft_skills: List[str]  # Communication, leadership, etc.
    domain_keywords: List[str]  # Industry-specific terms
    salary_range: Optional[str] = None


class InnomaticsJDParser:
    """
    Advanced Job Description Parser for Innomatics Research Labs
    Extracts structured information to enable precise resume-JD matching
    """
    
    def __init__(self):
        """Initialize the JD parser with NLP models and skill databases"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Please install: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Comprehensive skill databases for Indian tech industry
        self.technical_skills_db = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift',
                'scala', 'r', 'matlab', 'php', 'ruby', 'perl', 'shell scripting', 'bash'
            ],
            'web_technologies': [
                'react', 'angular', 'vue.js', 'nodejs', 'express', 'django', 'flask', 'spring boot',
                'html', 'css', 'scss', 'sass', 'bootstrap', 'tailwind', 'jquery', 'webpack'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
                'sqlite', 'oracle', 'sql server', 'neo4j', 'firebase'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform',
                'ansible', 'helm', 'openshift', 'cloudformation'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
                'numpy', 'matplotlib', 'seaborn', 'jupyter', 'apache spark', 'hadoop', 'kafka', 'airflow'
            ],
            'mobile_development': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova'
            ],
            'testing': [
                'selenium', 'junit', 'testng', 'pytest', 'jest', 'cypress', 'postman', 'jmeter'
            ]
        }
        
        self.soft_skills_db = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical thinking',
            'project management', 'time management', 'adaptability', 'creativity', 'attention to detail',
            'collaboration', 'mentoring', 'presentation', 'documentation', 'agile', 'scrum'
        ]
        
        # Common qualification patterns
        self.qualification_patterns = [
            r'(?:bachelor|b\.?tech|b\.?e\.?|bca|mca|m\.?tech|m\.?e\.?|mba|phd)',
            r'(?:computer science|information technology|electronics|electrical|mechanical)',
            r'(?:certification|certified|certificate)',
            r'(?:aws certified|azure certified|google certified|oracle certified)'
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)[\+\-\s]*(?:to|[\-\+])\s*(\d+)\s*years?',
            r'(\d+)[\+\-\s]*years?',
            r'minimum\s*(\d+)\s*years?',
            r'atleast\s*(\d+)\s*years?',
            r'(\d+)[\+\-\s]*yrs?'
        ]

    def parse_job_description(self, jd_text: str, role_title: str = "", company_name: str = "") -> JobDescriptionAnalysis:
        """
        Parse job description and extract structured information
        
        Args:
            jd_text: Full job description text
            role_title: Job role title
            company_name: Company name
            
        Returns:
            JobDescriptionAnalysis: Structured JD analysis
        """
        # Clean and preprocess text
        cleaned_text = self._clean_text(jd_text)
        
        # Extract different components
        must_have_skills = self._extract_must_have_skills(cleaned_text)
        good_to_have_skills = self._extract_good_to_have_skills(cleaned_text)
        qualifications = self._extract_qualifications(cleaned_text)
        experience_required = self._extract_experience_requirement(cleaned_text)
        responsibilities = self._extract_responsibilities(cleaned_text)
        technical_skills = self._extract_technical_skills(cleaned_text)
        soft_skills = self._extract_soft_skills(cleaned_text)
        domain_keywords = self._extract_domain_keywords(cleaned_text)
        salary_range = self._extract_salary_range(cleaned_text)
        
        return JobDescriptionAnalysis(
            role_title=role_title or self._extract_role_title(cleaned_text),
            company_name=company_name,
            must_have_skills=must_have_skills,
            good_to_have_skills=good_to_have_skills,
            qualifications=qualifications,
            experience_required=experience_required,
            role_responsibilities=responsibilities,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            domain_keywords=domain_keywords,
            salary_range=salary_range
        )

    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common JD formatting artifacts
        text = re.sub(r'job\s*description:?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'about\s*the\s*role:?', '', text, flags=re.IGNORECASE)
        
        return text

    def _extract_must_have_skills(self, text: str) -> List[str]:
        """Extract mandatory/critical skills from JD"""
        must_have_indicators = [
            r'must\s*have:?(.*?)(?:good\s*to\s*have|nice\s*to\s*have|preferred|desired|plus|\n\n|$)',
            r'required\s*skills?:?(.*?)(?:preferred|desired|plus|nice\s*to\s*have|\n\n|$)',
            r'mandatory:?(.*?)(?:preferred|desired|plus|\n\n|$)',
            r'essential:?(.*?)(?:preferred|desired|plus|\n\n|$)'
        ]
        
        must_have_skills = []
        for pattern in must_have_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                skills_text = match.group(1)
                skills = self._extract_skills_from_text(skills_text)
                must_have_skills.extend(skills)
        
        # If no explicit must-have section, extract from general skills
        if not must_have_skills:
            all_skills = self._extract_skills_from_text(text)
            # Take top technical skills as must-have
            must_have_skills = all_skills[:10]
        
        return list(set(must_have_skills))

    def _extract_good_to_have_skills(self, text: str) -> List[str]:
        """Extract nice-to-have/preferred skills from JD"""
        good_to_have_indicators = [
            r'(?:good\s*to\s*have|nice\s*to\s*have|preferred|desired|plus):?(.*?)(?:\n\n|$)',
            r'additional\s*skills?:?(.*?)(?:\n\n|$)',
            r'bonus:?(.*?)(?:\n\n|$)'
        ]
        
        good_to_have_skills = []
        for pattern in good_to_have_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                skills_text = match.group(1)
                skills = self._extract_skills_from_text(skills_text)
                good_to_have_skills.extend(skills)
        
        return list(set(good_to_have_skills))

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from a text chunk using skill databases"""
        skills = []
        text_lower = text.lower()
        
        # Check all skill categories
        for category, skill_list in self.technical_skills_db.items():
            for skill in skill_list:
                if skill in text_lower:
                    skills.append(skill)
        
        # Extract skills using patterns (e.g., bullet points)
        skill_patterns = [
            r'[•\-\*]\s*([^\n•\-\*]+)',  # Bullet points
            r'(\w+(?:\.\w+)*)\s*(?:,|$)',  # Comma-separated
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                skill = match.strip()
                if len(skill) > 2 and skill.lower() in text_lower:
                    skills.append(skill.lower())
        
        return list(set(skills))

    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract education and certification requirements"""
        qualifications = []
        
        for pattern in self.qualification_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            qualifications.extend(matches)
        
        # Extract common qualification phrases
        qual_phrases = [
            r'(?:bachelor|master|phd).*?(?:degree|certification)',
            r'(?:b\.?tech|m\.?tech|bca|mca).*?(?:computer|information|electronics)',
            r'(?:aws|azure|google|oracle)\s*certified.*?(?:associate|professional|expert)'
        ]
        
        for pattern in qual_phrases:
            matches = re.findall(pattern, text, re.IGNORECASE)
            qualifications.extend(matches)
        
        return list(set([q.strip() for q in qualifications if q.strip()]))

    def _extract_experience_requirement(self, text: str) -> str:
        """Extract experience requirements"""
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} years"
                else:
                    return f"{match.group(1)} years"
        
        return "Not specified"

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key job responsibilities"""
        responsibility_sections = [
            r'(?:responsibilities|duties|role):?(.*?)(?:requirements|qualifications|skills|\n\n|$)',
            r'(?:what you\'ll do|you will):?(.*?)(?:requirements|qualifications|skills|\n\n|$)'
        ]
        
        responsibilities = []
        for pattern in responsibility_sections:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                resp_text = match.group(1)
                # Extract bullet points
                bullet_points = re.findall(r'[•\-\*]\s*([^\n•\-\*]+)', resp_text)
                responsibilities.extend([r.strip() for r in bullet_points if r.strip()])
        
        return responsibilities[:8]  # Limit to top 8 responsibilities

    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills specifically"""
        technical_skills = []
        text_lower = text.lower()
        
        for category, skills in self.technical_skills_db.items():
            for skill in skills:
                if skill in text_lower:
                    technical_skills.append(skill)
        
        return list(set(technical_skills))

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills"""
        soft_skills = []
        text_lower = text.lower()
        
        for skill in self.soft_skills_db:
            if skill in text_lower:
                soft_skills.append(skill)
        
        return list(set(soft_skills))

    def _extract_domain_keywords(self, text: str) -> List[str]:
        """Extract domain-specific keywords"""
        # Use NLP to extract important entities and keywords
        if not self.nlp:
            return []
        
        doc = self.nlp(text.lower())
        
        # Extract named entities, noun phrases
        keywords = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'TECHNOLOGY']:
                keywords.append(ent.text)
        
        # Extract noun chunks that might be domain terms
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3 and len(chunk.text) > 3:
                keywords.append(chunk.text)
        
        return list(set(keywords[:20]))  # Top 20 domain keywords

    def _extract_role_title(self, text: str) -> str:
        """Extract role title if not provided"""
        # Look for common role title patterns
        title_patterns = [
            r'(?:role|position|title):\s*([^\n]+)',
            r'hiring\s*for\s*([^\n]+)',
            r'^([^\n]+?)(?:engineer|developer|analyst|manager)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return "Software Engineer"  # Default fallback

    def _extract_salary_range(self, text: str) -> Optional[str]:
        """Extract salary information if mentioned"""
        salary_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|k|thousand)',
            r'(?:salary|package|compensation):\s*([^\n]+)',
            r'(\d+)\s*(?:lpa|lakhs?)\s*(?:to|-)\s*(\d+)\s*(?:lpa|lakhs?)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None

    def get_jd_summary(self, analysis: JobDescriptionAnalysis) -> Dict[str, any]:
        """Generate a summary of JD analysis for quick review"""
        return {
            "role_title": analysis.role_title,
            "company": analysis.company_name,
            "experience_required": analysis.experience_required,
            "total_must_have_skills": len(analysis.must_have_skills),
            "total_good_to_have_skills": len(analysis.good_to_have_skills),
            "top_technical_skills": analysis.technical_skills[:5],
            "key_qualifications": analysis.qualifications,
            "complexity_score": self._calculate_complexity_score(analysis)
        }

    def _calculate_complexity_score(self, analysis: JobDescriptionAnalysis) -> int:
        """Calculate JD complexity (1-10 scale) based on requirements"""
        score = 0
        
        # Base score from skill requirements
        score += min(len(analysis.must_have_skills), 5)
        score += min(len(analysis.technical_skills), 3)
        
        # Experience requirement complexity
        if "senior" in analysis.role_title.lower() or "lead" in analysis.role_title.lower():
            score += 2
        
        return min(score, 10)