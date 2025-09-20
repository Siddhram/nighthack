# Resume Relevance Check System

A comprehensive AI-powered resume evaluation system built for Innomatics Research Labs to automate and streamline the resume screening process against job requirements.

![System Architecture](https://img.shields.io/badge/Architecture-Full--Stack-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-React-blue)
![AI](https://img.shields.io/badge/AI-LangChain%20%2B%20Transformers-purple)

## 🚀 Features

### Core Functionality
- **Automated Resume Parsing**: Extract skills, experience, education, and projects from PDF/DOCX files
- **Job Description Analysis**: Parse and structure job requirements and skills
- **AI-Powered Evaluation**: Hybrid scoring using hard matching and semantic similarity
- **Relevance Scoring**: Generate 0-100 relevance scores with detailed feedback
- **Suitability Classification**: High/Medium/Low fit verdicts for recruiters
- **Gap Analysis**: Identify missing skills and qualifications

### Dashboard & Analytics
- **Real-time Dashboard**: Overview of system performance and statistics
- **Candidate Management**: Track and manage all uploaded resumes
- **Job Management**: Create and manage job postings
- **Evaluation Results**: Detailed analysis and recommendations
- **Performance Metrics**: Track hiring pipeline effectiveness

### Technical Features
- **Scalable Architecture**: Handle thousands of resumes weekly
- **RESTful API**: Well-documented FastAPI backend
- **Modern UI**: Beautiful React frontend with Tailwind CSS
- **Database Integration**: SQLite for development, PostgreSQL-ready
- **File Processing**: Support for PDF and DOCX resume formats
- **Real-time Updates**: Live dashboard with evaluation progress

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend │    │   AI/ML Engine  │
│                 │    │                  │    │                 │
│ • Dashboard     │◄──►│ • REST APIs      │◄──►│ • Resume Parser │
│ • Job Management│    │ • File Upload    │    │ • Evaluation    │
│ • Resume Upload │    │ • Authentication │    │ • Scoring       │
│ • Results View  │    │ • Data Models    │    │ • Feedback Gen  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   SQLite DB     │    │   Vector Store  │
                       │                 │    │                 │
                       │ • Jobs          │    │ • Embeddings    │
                       │ • Resumes       │    │ • Semantic      │
                       │ • Evaluations   │    │   Search        │
                       │ • Analytics     │    │ • Similarity    │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **File Processing**: PyMuPDF, python-docx
- **NLP**: spaCy, NLTK
- **AI/ML**: LangChain, Sentence Transformers, scikit-learn
- **Vector Store**: ChromaDB, FAISS
- **API**: OpenAI GPT-3.5/4

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI, Heroicons
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **Routing**: React Router

### Development
- **Package Management**: pip (Python), npm (Node.js)
- **Environment**: Virtual environments, dotenv
- **Development Server**: Uvicorn (backend), Vite (frontend)

## 📦 Installation & Setup

### Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- **OpenAI API Key** (for advanced semantic matching)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd resume-relevance-system
```

2. **Run the automated setup**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Configure environment**
```bash
# Edit backend/.env and add your OpenAI API key
cp backend/.env.example backend/.env
# Edit the OPENAI_API_KEY in backend/.env
```

4. **Start development servers**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///./resume_system.db

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS
FRONTEND_URL=http://localhost:3000

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,docx

# AI Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
SIMILARITY_THRESHOLD=0.7

# Scoring Weights
HARD_MATCH_WEIGHT=0.4
SEMANTIC_MATCH_WEIGHT=0.6
```

## 📚 API Documentation

### Core Endpoints

#### Jobs
- `POST /api/jobs/` - Create a new job
- `GET /api/jobs/` - List all jobs
- `GET /api/jobs/{id}` - Get specific job
- `PUT /api/jobs/{id}` - Update job
- `DELETE /api/jobs/{id}` - Delete job

#### Resumes
- `POST /api/resumes/upload` - Upload and parse resume
- `GET /api/resumes/` - List all resumes
- `GET /api/resumes/{id}` - Get specific resume
- `DELETE /api/resumes/{id}` - Delete resume

#### Evaluations
- `POST /api/evaluations/evaluate` - Evaluate resume against job
- `GET /api/evaluations/` - List evaluations with filters
- `GET /api/evaluations/{id}` - Get specific evaluation
- `DELETE /api/evaluations/{id}` - Delete evaluation

#### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/job-performance/{job_id}` - Get job performance metrics
- `GET /api/dashboard/top-candidates/{job_id}` - Get top candidates for job

### Example API Usage

#### Upload Resume
```bash
curl -X POST "http://localhost:8000/api/resumes/upload" \
     -F "file=@resume.pdf" \
     -F "candidate_name=John Doe" \
     -F "email=john@example.com"
```

#### Evaluate Resume
```bash
curl -X POST "http://localhost:8000/api/evaluations/evaluate?job_id=1&resume_id=1"
```

## 🧠 AI Evaluation Engine

### Evaluation Process

1. **Resume Parsing**
   - Text extraction from PDF/DOCX
   - Skills identification using NLP
   - Experience and education parsing
   - Project and certification extraction

2. **Job Analysis**
   - Requirement extraction
   - Skill categorization
   - Priority weighting

3. **Scoring Algorithm**
   - **Hard Match (40%)**: Exact skill matching with fuzzy logic
   - **Semantic Match (60%)**: Embedding-based similarity using Sentence Transformers
   - **Final Score**: Weighted combination (0-100 scale)

4. **Classification**
   - **High (80-100)**: Strong match, recommend for interview
   - **Medium (60-79)**: Good potential, consider with context
   - **Low (0-59)**: Poor match, likely not suitable

5. **Feedback Generation**
   - Personalized improvement suggestions
   - Gap analysis with specific recommendations
   - Skills development roadmap

## 📊 Dashboard Features

### Key Metrics
- Total active jobs and applications
- Resume upload and processing statistics
- Evaluation completion rates
- Match quality distribution
- System performance metrics

### Visualizations
- Candidate suitability pie charts
- Score distribution histograms
- Time-series evaluation trends
- Job performance comparisons

## 🎯 Use Cases

### For Placement Teams
- **Bulk Screening**: Process hundreds of resumes efficiently
- **Quality Control**: Consistent evaluation criteria
- **Performance Tracking**: Monitor hiring pipeline effectiveness
- **Candidate Shortlisting**: Automated filtering and ranking

### For Students/Candidates
- **Profile Analysis**: Understand resume strength
- **Skill Gap Identification**: Know what skills to develop
- **Improvement Feedback**: Actionable recommendations
- **Market Insight**: Understand job market requirements

## 🚀 Quick Start

1. **Setup**: `./setup.sh`
2. **Configure**: Edit `backend/.env` with OpenAI API key
3. **Start**: `./start-dev.sh`
4. **Access**: http://localhost:3000

## 📞 Contact

For questions, suggestions, or support:
- **Project**: Innomatics Research Labs
- **Documentation**: Available at `/docs` when running

---

**Built with ❤️ for efficient, fair, and intelligent resume screening.**