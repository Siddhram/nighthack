# Resume Relevance Check System

An AI-powered system that automatically evaluates resume relevance against job requirements, providing scores, feedback, and actionable insights for placement teams and candidates.

## 🎯 Problem Statement

At Innomatics Research Labs, resume evaluation is currently manual, inconsistent, and time-consuming. The placement team across multiple locations receives 18-20 job requirements weekly, each attracting thousands of applications. This system automates the evaluation process to provide:

- **Automated resume evaluation** against job requirements at scale
- **Relevance Score (0-100)** for each resume per job role
- **Gap analysis** highlighting missing skills, certifications, or projects
- **Fit verdict** (High/Medium/Low suitability) for recruiters
- **Personalized improvement feedback** for students
- **Web-based dashboard** for placement team management

## ✨ Features

### 🤖 AI-Powered Evaluation
- **Hybrid Scoring System**: Combines rule-based checks with LLM semantic understanding
- **Hard Matching**: Keyword and skill matching with fuzzy logic
- **Semantic Matching**: Embedding-based similarity using transformer models
- **LangChain Integration**: Structured workflows for resume-JD analysis

### 📊 Comprehensive Analysis
- **Skills Gap Analysis**: Identifies missing technical and soft skills
- **Qualification Matching**: Education and certification requirements
- **Experience Assessment**: Years of experience and role relevance
- **Project Portfolio Review**: Relevant project experience evaluation

### 🎨 Beautiful User Interface
- **Modern React Dashboard**: Built with TypeScript and Tailwind CSS
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Updates**: Live evaluation progress and results
- **Data Visualization**: Charts and graphs for evaluation insights

### 🔧 Robust Backend
- **FastAPI Framework**: High-performance async API
- **SQLite Database**: Efficient data storage and retrieval
- **File Processing**: PDF/DOCX resume parsing
- **Vector Search**: Semantic similarity using embeddings

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │────│   FastAPI       │────│   AI Services   │
│   - Dashboard    │    │   - REST API    │    │   - OpenAI/LLM  │
│   - File Upload  │    │   - File Proc.  │    │   - Embeddings  │
│   - Results View │    │   - Database    │    │   - NLP Pipeline│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** - Core language
- **FastAPI** - Web framework
- **SQLAlchemy** - Database ORM
- **PyMuPDF / python-docx** - Document processing
- **spaCy / NLTK** - Natural language processing
- **LangChain** - LLM workflow orchestration
- **Sentence Transformers** - Text embeddings
- **OpenAI GPT** - Language model for semantic analysis

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **Axios** - HTTP client
- **React Router** - Navigation
- **Recharts** - Data visualization
- **React Hot Toast** - Notifications

### AI & ML
- **OpenAI GPT-3.5/4** - Language understanding
- **Sentence-BERT** - Text embeddings
- **scikit-learn** - ML utilities
- **Chroma/FAISS** - Vector databases
- **Fuzzy String Matching** - Skill matching

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- OpenAI API key (for AI features)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

6. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   ```
   http://localhost:3000
   ```

## 📖 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/` | Create new job posting |
| GET | `/api/jobs/` | List all jobs |
| POST | `/api/resumes/upload` | Upload resume file |
| POST | `/api/evaluations/evaluate` | Evaluate resume against job |
| GET | `/api/evaluations/` | Get evaluation results |
| GET | `/api/dashboard/stats` | Dashboard statistics |

## 💼 Usage Workflow

### 1. Job Posting Upload
- Placement team uploads job descriptions
- System extracts required skills, qualifications, and experience
- Creates structured job profile

### 2. Resume Submission
- Students upload resumes (PDF/DOCX)
- System extracts and parses resume content
- Identifies skills, experience, education, and projects

### 3. AI Evaluation
- **Hard Matching**: Exact skill keyword matching
- **Semantic Analysis**: AI-powered content understanding
- **Scoring Algorithm**: Weighted combination of matches
- **Feedback Generation**: Personalized improvement suggestions

### 4. Results Dashboard
- View evaluation scores and rankings
- Filter candidates by suitability level
- Export shortlisted candidates
- Track evaluation metrics

## 🎯 Scoring Algorithm

The system uses a hybrid approach:

```python
final_score = (hard_match_score * 0.4) + (semantic_match_score * 0.6)
```

### Hard Matching (40% weight)
- Exact keyword matches
- Skill name variations
- Fuzzy string matching
- Certification matching

### Semantic Matching (60% weight)
- Embedding similarity
- Contextual understanding
- Role-specific requirements
- Experience relevance

### Suitability Levels
- **High (80-100)**: Strong match, recommended for interview
- **Medium (60-79)**: Good potential, consider for review
- **Low (0-59)**: Significant gaps, provide feedback

## 🔒 Security & Privacy

- File uploads are securely stored and processed
- Personal information is handled according to privacy standards
- Database access is controlled and logged
- API endpoints include proper authentication mechanisms

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Sample Data Structure

### Resume Data
```json
{
  "candidate_name": "John Doe",
  "email": "john.doe@email.com",
  "skills": ["Python", "React", "Machine Learning"],
  "experience": [
    {
      "title": "Software Developer",
      "company": "Tech Corp",
      "duration": "2 years",
      "technologies": ["Python", "Django", "PostgreSQL"]
    }
  ],
  "education": [
    {
      "degree": "B.Tech Computer Science",
      "institution": "University XYZ",
      "year": "2022"
    }
  ]
}
```

### Evaluation Result
```json
{
  "relevance_score": 87.5,
  "hard_match_score": 82.0,
  "semantic_match_score": 91.0,
  "suitability": "High",
  "matched_skills": ["Python", "React", "Git"],
  "missing_skills": ["Docker", "AWS", "Kubernetes"],
  "feedback": "Strong technical background with relevant experience..."
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [API documentation](http://localhost:8000/docs)
- Review the troubleshooting guide below

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.9+)
- Ensure all dependencies are installed
- Verify database permissions
- Check OpenAI API key configuration

**Frontend build fails:**
- Clear node_modules and reinstall
- Check Node.js version (18+)
- Verify Tailwind CSS configuration

**AI evaluation errors:**
- Verify OpenAI API key
- Check network connectivity
- Review API rate limits
- Ensure model availability

**File upload issues:**
- Check file size limits (10MB default)
- Verify file format (PDF/DOCX only)
- Ensure upload directory permissions

---

Built with ❤️ for efficient and intelligent recruitment processes.