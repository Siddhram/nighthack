import re
import spacy
import PyPDF2
from docx import Document
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResumeAnalysis:
    """Comprehensive resume analysis for Innomatics Research Labs"""
    student_name: str
    contact_info: Dict[str, str]  # email, phone, location
    extracted_skills: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    work_experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    certifications: List[str]
    total_experience_years: float
    achievements: List[str]
    github_links: List[str]
    linkedin_profile: Optional[str]
    resume_quality_score: float  # 1-10
    parsed_text: str


class InnomaticsResumeAnalyzer:
    """
    Advanced Resume Analyzer for Innomatics Research Labs
    Extracts structured information from student resumes for precise JD matching
    """
    
    def __init__(self):
        """Initialize the resume analyzer with NLP models and databases"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Please install: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Comprehensive skill databases (same as JD parser for consistency)
        self.technical_skills_db = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift',
                'scala', 'r', 'matlab', 'php', 'ruby', 'perl', 'shell scripting', 'bash'
            ],
            'web_technologies': [
                'react', 'angular', 'vue.js', 'nodejs', 'express', 'django', 'flask', 'spring boot',
                'html', 'css', 'scss', 'sass', 'bootstrap', 'tailwind', 'jquery', 'webpack', 'nextjs'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
                'sqlite', 'oracle', 'sql server', 'neo4j', 'firebase', 'supabase'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform',
                'ansible', 'helm', 'openshift', 'cloudformation', 'github actions', 'gitlab ci'
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
            ],
            'tools_frameworks': [
                'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'trello', 'figma', 'photoshop'
            ]
        }
        
        self.soft_skills_db = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical thinking',
            'project management', 'time management', 'adaptability', 'creativity', 'attention to detail',
            'collaboration', 'mentoring', 'presentation', 'documentation', 'agile', 'scrum'
        ]
        
        # Indian education system patterns
        self.education_patterns = [
            r'(?:b\.?tech|bachelor.*technology|b\.?e\.?|bachelor.*engineering)',
            r'(?:m\.?tech|master.*technology|m\.?e\.?|master.*engineering)',
            r'(?:bca|bachelor.*computer.*application)',
            r'(?:mca|master.*computer.*application)',
            r'(?:mba|master.*business.*administration)',
            r'(?:phd|doctorate)',
            r'(?:diploma|polytechnic)',
            r'(?:12th|intermediate|higher.*secondary)',
            r'(?:10th|matriculation|secondary)'
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'experience.*?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
            r'(\d{4})\s*(?:to|-|–)\s*(?:present|current|\d{4})',  # Date ranges
            r'(?:from|since)\s*(\d{4})',
            r'(\d+)\s*months?\s*(?:of\s*)?experience'
        ]
        
        # Project indicators
        self.project_indicators = [
            'project', 'built', 'developed', 'created', 'implemented', 'designed',
            'worked on', 'contributed to', 'led', 'managed'
        ]

    def analyze_resume(self, file_path: str, filename: str) -> ResumeAnalysis:
        """
        Comprehensive resume analysis
        
        Args:
            file_path: Path to resume file
            filename: Original filename
            
        Returns:
            ResumeAnalysis: Structured resume analysis
        """
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = self._extract_text_from_pdf(file_path)
        elif filename.lower().endswith(('.docx', '.doc')):
            text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        if not text or len(text.strip()) < 100:
            raise ValueError("Resume text too short or extraction failed")
        
        # Clean and preprocess text
        cleaned_text = self._clean_text(text)
        
        # Extract all components
        student_name = self._extract_name(cleaned_text)
        contact_info = self._extract_contact_info(cleaned_text)
        skills = self._extract_skills(cleaned_text)
        work_experience = self._extract_work_experience(cleaned_text)
        education = self._extract_education(cleaned_text)
        projects = self._extract_projects(cleaned_text)
        certifications = self._extract_certifications(cleaned_text)
        total_experience = self._calculate_total_experience(work_experience, cleaned_text)
        achievements = self._extract_achievements(cleaned_text)
        links = self._extract_links(cleaned_text)
        quality_score = self._calculate_resume_quality(cleaned_text, skills, work_experience, education, projects)
        
        return ResumeAnalysis(
            student_name=student_name,
            contact_info=contact_info,
            extracted_skills=skills['all_skills'],
            technical_skills=skills['technical_skills'],
            soft_skills=skills['soft_skills'],
            work_experience=work_experience,
            education=education,
            projects=projects,
            certifications=certifications,
            total_experience_years=total_experience,
            achievements=achievements,
            github_links=links['github'],
            linkedin_profile=links['linkedin'],
            resume_quality_score=quality_score,
            parsed_text=cleaned_text
        )

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize resume text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common resume artifacts
        text = re.sub(r'page\s*\d+\s*of\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'resume|curriculum vitae|cv', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def _extract_name(self, text: str) -> str:
        """Extract candidate name from resume"""
        # Try to find name patterns at the beginning
        lines = text.split('\n')[:5]  # Check first 5 lines
        
        name_patterns = [
            r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)',  # First line with proper case
            r'name:\s*([A-Za-z\s]+)',  # Explicit name field
            r'^([A-Z\s]{2,30})$'  # All caps name on separate line
        ]
        
        for line in lines:
            line = line.strip()
            for pattern in name_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if 2 <= len(name.split()) <= 4 and all(part.isalpha() for part in name.split()):
                        return name
        
        return "Name Not Found"

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information (email, phone, location)"""
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        contact_info['email'] = email_match.group() if email_match else ""
        
        # Phone extraction (Indian formats)
        phone_patterns = [
            r'\+91[\s-]?\d{10}',
            r'\b\d{10}\b',
            r'\(\+91\)[\s-]?\d{10}',
            r'\b\d{3}[\s-]\d{3}[\s-]\d{4}\b'
        ]
        
        phone_number = ""
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                phone_number = phone_match.group()
                break
        contact_info['phone'] = phone_number
        
        # Location extraction (Indian cities)
        indian_cities = [
            'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune', 'ahmedabad',
            'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane', 'bhopal',
            'visakhapatnam', 'pimpri', 'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik'
        ]
        
        location = ""
        text_lower = text.lower()
        for city in indian_cities:
            if city in text_lower:
                location = city.title()
                break
        
        contact_info['location'] = location
        
        return contact_info

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills"""
        text_lower = text.lower()
        
        technical_skills = []
        for category, skill_list in self.technical_skills_db.items():
            for skill in skill_list:
                if skill in text_lower:
                    technical_skills.append(skill)
        
        soft_skills = []
        for skill in self.soft_skills_db:
            if skill in text_lower:
                soft_skills.append(skill)
        
        # Extract skills from skills section specifically
        skills_section_match = re.search(
            r'(?:skills?|technologies?|technical\s*skills?):\s*(.*?)(?:\n[A-Z]|$)', 
            text, re.IGNORECASE | re.DOTALL
        )
        
        additional_skills = []
        if skills_section_match:
            skills_text = skills_section_match.group(1)
            # Extract comma-separated skills
            skill_candidates = re.split(r'[,\n•\-\|]', skills_text)
            for skill in skill_candidates:
                skill = skill.strip().lower()
                if skill and len(skill) > 1 and skill not in technical_skills:
                    additional_skills.append(skill)
        
        all_skills = list(set(technical_skills + soft_skills + additional_skills))
        
        return {
            'all_skills': all_skills,
            'technical_skills': list(set(technical_skills)),
            'soft_skills': list(set(soft_skills))
        }

    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience details"""
        # Find experience section
        experience_sections = re.findall(
            r'(?:experience|employment|work\s*history):(.*?)(?:\n(?:[A-Z][a-z]+\s*:|\Z))',
            text, re.IGNORECASE | re.DOTALL
        )
        
        experiences = []
        
        for section in experience_sections:
            # Look for job entries with company, role, dates
            job_entries = re.findall(
                r'([^\n]+)\s*(?:at|@)\s*([^\n]+)\s*\(([^)]+)\)',
                section, re.IGNORECASE
            )
            
            for role, company, duration in job_entries:
                exp_dict = {
                    'role': role.strip(),
                    'company': company.strip(),
                    'duration': duration.strip(),
                    'years': self._extract_years_from_duration(duration)
                }
                experiences.append(exp_dict)
        
        # If no structured experience found, look for general patterns
        if not experiences:
            # Look for role-company patterns
            role_patterns = re.findall(
                r'(?:software\s*engineer|developer|analyst|intern|trainee|consultant).*?(?:at|@)\s*([^\n]+)',
                text, re.IGNORECASE
            )
            
            for i, company in enumerate(role_patterns[:3]):  # Max 3 experiences
                experiences.append({
                    'role': 'Software Engineer' if 'engineer' in text.lower() else 'Developer',
                    'company': company.strip(),
                    'duration': 'Duration not specified',
                    'years': 0.5  # Default assumption
                })
        
        return experiences

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education details"""
        education_list = []
        
        # Find education section
        education_section = re.search(
            r'(?:education|academic|qualification):\s*(.*?)(?:\n(?:[A-Z][a-z]+\s*:|\Z))',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if education_section:
            edu_text = education_section.group(1)
            
            # Extract degree patterns
            for pattern in self.education_patterns:
                matches = re.finditer(pattern, edu_text, re.IGNORECASE)
                for match in matches:
                    degree = match.group()
                    
                    # Try to find associated college/university
                    context = edu_text[max(0, match.start()-100):match.end()+100]
                    
                    # Look for institution names
                    institution_patterns = [
                        r'(?:from|at)\s*([^\n,]+(?:university|college|institute|iit|nit|iiit))',
                        r'([^\n,]+(?:university|college|institute|iit|nit|iiit))'
                    ]
                    
                    institution = "Institution not specified"
                    for inst_pattern in institution_patterns:
                        inst_match = re.search(inst_pattern, context, re.IGNORECASE)
                        if inst_match:
                            institution = inst_match.group(1).strip()
                            break
                    
                    # Extract graduation year
                    year_match = re.search(r'(\d{4})', context)
                    year = year_match.group(1) if year_match else "Year not specified"
                    
                    education_list.append({
                        'degree': degree,
                        'institution': institution,
                        'year': year,
                        'field': self._extract_field_of_study(context)
                    })
        
        # If no education found in section, look globally
        if not education_list:
            for pattern in self.education_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    education_list.append({
                        'degree': match.group(),
                        'institution': 'Not specified',
                        'year': 'Not specified',
                        'field': 'Computer Science'  # Default assumption
                    })
                    break
        
        return education_list

    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project details"""
        projects = []
        
        # Find projects section
        project_section = re.search(
            r'(?:projects?|portfolio):\s*(.*?)(?:\n(?:[A-Z][a-z]+\s*:|\Z))',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if project_section:
            proj_text = project_section.group(1)
            
            # Look for project entries (usually with titles and descriptions)
            project_entries = re.findall(
                r'(?:^|\n)([^\n]+?)(?:\s*-\s*|\s*:\s*|\n)(.*?)(?=\n[^\n]+?(?:\s*-\s*|\s*:\s*)|\Z)',
                proj_text, re.MULTILINE | re.DOTALL
            )
            
            for title, description in project_entries:
                if any(indicator in title.lower() for indicator in self.project_indicators):
                    # Extract technologies used
                    tech_used = []
                    desc_lower = description.lower()
                    for category, skills in self.technical_skills_db.items():
                        for skill in skills:
                            if skill in desc_lower:
                                tech_used.append(skill)
                    
                    projects.append({
                        'title': title.strip(),
                        'description': description.strip()[:200] + "..." if len(description) > 200 else description.strip(),
                        'technologies': list(set(tech_used))[:5],  # Top 5 technologies
                        'type': 'Academic' if any(word in title.lower() for word in ['academic', 'college', 'university']) else 'Personal'
                    })
        
        # If no projects section, look for project indicators throughout text
        if not projects:
            for indicator in self.project_indicators[:3]:  # Check top 3 indicators
                pattern = rf'{indicator}\s+([^.]+\.)'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:  # Max 2 projects per indicator
                    projects.append({
                        'title': f'Project involving {indicator}',
                        'description': match.strip(),
                        'technologies': [],
                        'type': 'Inferred'
                    })
        
        return projects[:5]  # Limit to top 5 projects

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'(?:aws|amazon)\s*(?:certified|certification).*?(?:associate|professional|cloud|solution)',
            r'(?:azure|microsoft)\s*(?:certified|certification).*?(?:associate|expert|fundamentals)',
            r'(?:google|gcp)\s*(?:certified|certification).*?(?:associate|professional)',
            r'(?:oracle|java)\s*(?:certified|certification)',
            r'(?:cisco|ccna|ccnp)',
            r'(?:pmp|project management professional)',
            r'(?:cissp|security)',
            r'(?:kubernetes|docker)\s*(?:certified|certification)'
        ]
        
        text_lower = text.lower()
        for pattern in cert_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            certifications.extend(matches)
        
        # Look for certification section
        cert_section = re.search(
            r'(?:certification|certificate)s?:\s*(.*?)(?:\n[A-Z]|$)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if cert_section:
            cert_text = cert_section.group(1)
            # Extract bullet points or comma-separated items
            cert_items = re.split(r'[,\n•\-]', cert_text)
            for cert in cert_items:
                cert = cert.strip()
                if cert and len(cert) > 5:
                    certifications.append(cert)
        
        return list(set(certifications))

    def _calculate_total_experience(self, work_experience: List[Dict], text: str) -> float:
        """Calculate total years of experience"""
        if work_experience:
            total_years = sum(exp.get('years', 0) for exp in work_experience)
            return total_years
        
        # Fallback: extract from text patterns
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if 'month' in match.group():
                        months = float(re.search(r'(\d+)', match.group()).group(1))
                        return months / 12
                    else:
                        years = float(re.search(r'(\d+(?:\.\d+)?)', match.group()).group(1))
                        return years
                except:
                    continue
        
        # Default for fresh graduates
        return 0.0

    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and accomplishments"""
        achievements = []
        
        achievement_indicators = [
            'awarded', 'won', 'achieved', 'recognized', 'selected', 'published',
            'presented', 'led', 'increased', 'improved', 'reduced', 'implemented'
        ]
        
        for indicator in achievement_indicators:
            pattern = rf'{indicator}\s+([^.]+\.)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    achievements.append(match.strip())
        
        return list(set(achievements))[:5]  # Top 5 achievements

    def _extract_links(self, text: str) -> Dict[str, Any]:
        """Extract GitHub and LinkedIn links"""
        links = {'github': [], 'linkedin': None}
        
        # GitHub links
        github_pattern = r'(?:github\.com/|git@github\.com:)([a-zA-Z0-9_-]+)'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        links['github'] = [f"https://github.com/{match}" for match in github_matches]
        
        # LinkedIn profile
        linkedin_pattern = r'(?:linkedin\.com/in/)([a-zA-Z0-9_-]+)'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            links['linkedin'] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
        
        return links

    def _calculate_resume_quality(self, text: str, skills: Dict, experience: List, education: List, projects: List) -> float:
        """Calculate resume quality score (1-10)"""
        score = 0.0
        
        # Basic information completeness (2 points)
        if len(text) > 500:
            score += 1
        if '@' in text and re.search(r'\d{10}', text):  # Email and phone
            score += 1
        
        # Skills diversity (2 points)
        if len(skills['technical_skills']) >= 5:
            score += 1
        if len(skills['all_skills']) >= 10:
            score += 1
        
        # Experience quality (2 points)
        if experience:
            score += 1
            if len(experience) >= 2:
                score += 1
        
        # Education (1 point)
        if education:
            score += 1
        
        # Projects (2 points)
        if projects:
            score += 1
            if len(projects) >= 2:
                score += 1
        
        # Professional links (1 point)
        if 'github.com' in text or 'linkedin.com' in text:
            score += 1
        
        return min(score, 10.0)

    def _extract_years_from_duration(self, duration: str) -> float:
        """Extract years from duration string"""
        duration_lower = duration.lower()
        
        # Look for year patterns
        year_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', duration_lower)
        if year_match:
            return float(year_match.group(1))
        
        # Look for month patterns
        month_match = re.search(r'(\d+)\s*(?:months?|mon)', duration_lower)
        if month_match:
            return float(month_match.group(1)) / 12
        
        # Date range patterns
        date_pattern = r'(\d{4})\s*(?:to|-|–)\s*(?:present|current|(\d{4}))'
        date_match = re.search(date_pattern, duration_lower)
        if date_match:
            start_year = int(date_match.group(1))
            end_year = int(date_match.group(2)) if date_match.group(2) else datetime.now().year
            return max(0, end_year - start_year)
        
        return 1.0  # Default assumption

    def _extract_field_of_study(self, context: str) -> str:
        """Extract field of study from education context"""
        fields = [
            'computer science', 'information technology', 'electronics', 'electrical',
            'mechanical', 'civil', 'chemical', 'biotechnology', 'mathematics',
            'physics', 'business administration', 'commerce'
        ]
        
        context_lower = context.lower()
        for field in fields:
            if field in context_lower:
                return field.title()
        
        return 'Computer Science'  # Default assumption for tech resumes

    def get_resume_summary(self, analysis: ResumeAnalysis) -> Dict[str, Any]:
        """Generate resume summary for quick review"""
        return {
            "student_name": analysis.student_name,
            "total_experience_years": analysis.total_experience_years,
            "technical_skills_count": len(analysis.technical_skills),
            "top_technical_skills": analysis.technical_skills[:5],
            "education_level": analysis.education[0]['degree'] if analysis.education else 'Not specified',
            "projects_count": len(analysis.projects),
            "certifications_count": len(analysis.certifications),
            "resume_quality_score": analysis.resume_quality_score,
            "contact_info": analysis.contact_info,
            "has_github": bool(analysis.github_links),
            "has_linkedin": bool(analysis.linkedin_profile)
        }