import PyPDF2
from io import BytesIO
from docx import Document
import re
# import spacy  # Commented out for now to avoid dependency conflicts
from typing import Dict, List, Any
import os


class ResumeParser:
    """Parse resume documents and extract structured information"""
    
    def __init__(self):
        """Initialize the resume parser with NLP model"""
        # try:
        #     self.nlp = spacy.load("en_core_web_sm")
        # except OSError:
        #     print("Warning: spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
        #     self.nlp = None
        
        # Using regex-based parsing for now
        self.nlp = None
        
        # Common skill patterns and keywords
        self.skill_patterns = [
            # Programming Languages
            r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin|Scala|R|MATLAB|SQL)\b',
            
            # Web Technologies
            r'\b(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|ASP\.NET|Laravel|Ruby on Rails)\b',
            
            # Databases
            r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQL Server|SQLite|Elasticsearch|Cassandra|DynamoDB)\b',
            
            # Cloud & DevOps
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|GitLab|GitHub|Terraform|Ansible|Vagrant)\b',
            
            # Data Science & AI
            r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Matplotlib|Jupyter|Apache Spark|Hadoop|Tableau)\b',
            
            # Mobile Development
            r'\b(?:iOS|Android|React Native|Flutter|Xamarin|Ionic|Cordova)\b',
            
            # Tools & Technologies
            r'\b(?:Git|Linux|Unix|Windows|macOS|Agile|Scrum|JIRA|Confluence|Slack|Figma|Adobe Creative Suite)\b'
        ]
        
        # Education patterns
        self.education_patterns = [
            r'\b(?:Bachelor|Master|PhD|Doctorate|B\.Tech|M\.Tech|B\.Sc|M\.Sc|MBA|B\.A|M\.A|B\.E|M\.E)\b',
            r'\b(?:Computer Science|Engineering|Information Technology|Software|Mathematics|Statistics|Physics)\b'
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\s*\+\s*(?:years?|yrs?)',
            r'(\d{4})\s*-\s*(\d{4}|\w+)',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}'
        ]

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""

    def extract_text(self, file_path: str) -> str:
        """Extract text from file based on extension"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\@\+\#]', ' ', text)
        
        return text

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using pattern matching"""
        skills = set()
        text_upper = text.upper()
        
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        # Additional manual skill extraction for common variations
        manual_skills = {
            'MACHINE LEARNING': ['ML', 'Machine Learning', 'machine learning'],
            'ARTIFICIAL INTELLIGENCE': ['AI', 'Artificial Intelligence'],
            'REACT.JS': ['React', 'ReactJS', 'React.js'],
            'NODE.JS': ['Node', 'NodeJS', 'Node.js'],
            'JAVASCRIPT': ['JS'],
            'TYPESCRIPT': ['TS'],
        }
        
        for canonical_skill, variations in manual_skills.items():
            for variation in variations:
                if variation.upper() in text_upper:
                    skills.add(canonical_skill)
                    break
        
        return list(skills)

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from text"""
        education = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for degree patterns
            for pattern in self.education_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Try to extract more context from surrounding lines
                    context_lines = lines[max(0, i-1):min(len(lines), i+3)]
                    context = ' '.join(context_lines)
                    
                    # Extract degree, institution, year
                    degree_match = re.search(r'\b(Bachelor|Master|PhD|Doctorate|B\.Tech|M\.Tech|B\.Sc|M\.Sc|MBA|B\.A|M\.A|B\.E|M\.E)[^,\n]*', context, re.IGNORECASE)
                    year_match = re.search(r'\b(19|20)\d{2}\b', context)
                    
                    edu_entry = {
                        'degree': degree_match.group(0).strip() if degree_match else line.strip(),
                        'institution': '',  # Could be improved with institution detection
                        'year': year_match.group(0) if year_match else ''
                    }
                    
                    # Avoid duplicates
                    if edu_entry not in education:
                        education.append(edu_entry)
                    break
        
        return education

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from text"""
        experience = []
        
        # Look for experience duration patterns
        total_years = 0
        year_matches = re.findall(r'(\d+)\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if year_matches:
            total_years = max([int(match) for match in year_matches])
        
        # Extract job titles (common patterns)
        job_title_patterns = [
            r'\b(Software Engineer|Developer|Programmer|Analyst|Manager|Lead|Senior|Junior)\b[^,\n]*',
            r'\b(Data Scientist|Machine Learning Engineer|DevOps Engineer|Full Stack Developer)\b[^,\n]*',
        ]
        
        job_titles = []
        for pattern in job_title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            job_titles.extend(matches)
        
        # For now, return a simplified structure
        if job_titles or total_years:
            experience.append({
                'total_years': total_years,
                'roles': list(set(job_titles))
            })
        
        return experience

    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information from text"""
        projects = []
        
        # Look for project keywords and surrounding context
        project_keywords = ['project', 'built', 'developed', 'created', 'implemented']
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in project_keywords):
                # Get some context around the project mention
                context_start = max(0, i-1)
                context_end = min(len(lines), i+2)
                context = ' '.join(lines[context_start:context_end]).strip()
                
                if len(context) > 20:  # Avoid very short matches
                    projects.append({
                        'description': context[:200] + '...' if len(context) > 200 else context
                    })
        
        # Remove duplicates and limit to reasonable number
        unique_projects = []
        seen = set()
        for project in projects:
            desc = project['description']
            if desc not in seen and len(unique_projects) < 5:
                unique_projects.append(project)
                seen.add(desc)
        
        return unique_projects

    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text"""
        certifications = []
        
        cert_patterns = [
            r'\b(AWS|Azure|Google Cloud|GCP)\s*(?:Certified|Certificate)[^,\n]*',
            r'\bCertified\s+[^,\n]*',
            r'\b(?:Certificate|Certification)\s+(?:in|of)\s+[^,\n]*',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
        
        return list(set(certifications))

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Phone pattern
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group(0)
        
        # Simple name extraction - look for the first line that looks like a name
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Skip empty lines and common headers
            if not line or line.lower() in ['resume', 'curriculum vitae', 'cv']:
                continue
            # Look for lines that could be names (2-4 words, mostly letters)
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.replace('.', '').replace(',', '').isalpha() for word in words):
                contact['name'] = line
                break
        
        return contact

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume file and extract structured information"""
        try:
            # Extract text from file
            text = self.extract_text(file_path)
            if not text:
                raise ValueError("No text could be extracted from the file")
            
            # Clean text
            clean_text = self.clean_text(text)
            
            # Extract various components
            skills = self.extract_skills(clean_text)
            education = self.extract_education(clean_text)
            experience = self.extract_experience(clean_text)
            projects = self.extract_projects(clean_text)
            certifications = self.extract_certifications(clean_text)
            contact_info = self.extract_contact_info(clean_text)
            
            return {
                'text': clean_text,
                'skills': skills,
                'education': education,
                'experience': experience,
                'projects': projects,
                'certifications': certifications,
                'contact_info': contact_info
            }
        
        except Exception as e:
            raise Exception(f"Failed to parse resume: {str(e)}")