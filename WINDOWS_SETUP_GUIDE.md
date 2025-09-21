# 🚀 Complete Setup & Running Guide - Windows

## 📋 Prerequisites

### Required Software:

1. **Python 3.9+** - [Download from python.org](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download from nodejs.org](https://nodejs.org/)
3. **Git** - [Download from git-scm.com](https://git-scm.com/downloads)

### Verify Installation:

```powershell
# Check Python version
python --version  # Should show 3.9+

# Check Node.js version
node --version    # Should show v18+

# Check npm version
npm --version
```

## 🔧 Initial Setup (One-time only)

### Step 1: Clone & Navigate

```powershell
# If you haven't cloned yet:
git clone <your-repo-url>
cd resume-relevance-system
```

### Step 2: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (CRITICAL STEP!)
.\venv\Scripts\activate

# Verify you're in virtual environment (you should see (venv) in prompt)
# Your prompt should look like: (venv) PS C:\path\to\resume-relevance-system\backend>

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env

# Create uploads directory
mkdir uploads -ErrorAction SilentlyContinue
```

### Step 3: Configure Environment Variables

Edit `backend\.env` file with your API keys:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./resume_system.db

# Pinecone Configuration (Already provided)
PINECONE_API_KEY=pcsk_4B27To_tY2jeLoxqgm97GKUfwxMccU39ZsN3jcd2D8Lq7UjZhjwEyHerwKDc8hpeinqpe
PINECONE_INDEX_NAME=lang
PINECONE_ENVIRONMENT=us-east-1

# Nomic AI Configuration (Already provided)
NOMIC_API_KEY=nk-LeXriqiihZl6pT8TT4QhSB8JQVhmJBAznO6Y-EaaDX4

# Google Gemini Configuration (REPLACE WITH YOUR KEY!)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Application Settings
APP_NAME=Resume Relevance Check System
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=["pdf", "docx"]
UPLOAD_DIR=uploads

# AI Settings
EMBEDDING_MODEL=nomic-embed-text-v1.5
LLM_MODEL=gemini-1.5-flash
SIMILARITY_THRESHOLD=0.7
EMBEDDING_DIMENSIONALITY=256

# Text Processing Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Scoring Weights
HARD_MATCH_WEIGHT=0.4
SEMANTIC_MATCH_WEIGHT=0.6
```

**🔑 IMPORTANT**: Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Step 4: Initialize Database

```powershell
# Make sure you're still in backend directory with venv activated
# Initialize the database tables
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database initialized successfully!')"
```

### Step 5: Frontend Setup

```powershell
# Navigate to frontend (open new terminal or deactivate venv)
cd ..\frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Method 1: Manual Start (Recommended for Development)

#### Terminal 1 - Backend Server:

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend Server:

```powershell
cd frontend
npm run dev
```

### Method 2: Alternative Backend Options

#### Option A: Run Standard Backend

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Run Pinecone + Gemini Backend (New AI Features)

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main_pinecone_gemini:app --reload --host 0.0.0.0 --port 8000
```

#### Option C: Run Simple Demo (For Testing)

```powershell
cd backend
.\venv\Scripts\activate
python pinecone_gemini_demo.py
```

## 🌐 Access Points

Once both servers are running:

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Alternative UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔧 Troubleshooting

### Common Issues & Solutions:

#### 1. **Virtual Environment Issues**

```powershell
# If activation fails:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
.\venv\Scripts\activate
```

#### 2. **Module Import Errors**

```powershell
# Make sure you're in virtual environment
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. **Database Issues**

```powershell
# Delete existing database and recreate
del resume_system.db
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database recreated!')"
```

#### 4. **Port Already in Use**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### 5. **Dependency Conflicts**

```powershell
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 6. **Frontend Issues**

```powershell
# Clear npm cache and reinstall
npm cache clean --force
del node_modules -Recurse -Force
del package-lock.json
npm install
```

## 📝 Development Workflow

### Starting Development Session:

```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Making Changes:

- **Backend**: FastAPI auto-reloads on file changes
- **Frontend**: Vite auto-reloads on file changes
- **Database**: Use Alembic for migrations (advanced usage)

### Testing API Endpoints:

1. Visit [http://localhost:8000/docs](http://localhost:8000/docs)
2. Use the interactive Swagger UI to test endpoints
3. Or use tools like Postman/Insomnia

## 🎯 Quick Test Workflow

### 1. Test Backend API:

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Or visit in browser: http://localhost:8000/docs
```

### 2. Test Frontend:

- Open [http://localhost:3000](http://localhost:3000)
- Navigate through Dashboard, Jobs, Resumes, Evaluations

### 3. Test Full Workflow:

1. **Create a Job**: Use Jobs page or API endpoint
2. **Upload Resume**: Use Upload Resume page
3. **Run Evaluation**: Use Evaluations API
4. **View Results**: Check Dashboard for statistics

## 🚨 Important Notes

### Security:

- **Never commit `.env` files** with real API keys
- Change default API keys in production
- Use environment-specific configurations

### Performance:

- SQLite is fine for development, consider PostgreSQL for production
- Monitor memory usage with large PDF files
- Consider Redis for caching in production

### Backup:

- Regularly backup `resume_system.db`
- Keep uploaded files in `backend/uploads/` backed up

## 🔄 Production Deployment

### Docker Deployment:

```dockerfile
# Example Dockerfile for backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup:

- Use proper environment variables
- Set up reverse proxy (nginx)
- Configure SSL certificates
- Set up monitoring and logging

## 📞 Support

If you encounter issues:

1. **Check Terminal Output**: Look for error messages
2. **Verify Prerequisites**: Ensure Python 3.9+ and Node.js 18+
3. **Check Virtual Environment**: Ensure `(venv)` shows in prompt
4. **Verify API Keys**: Ensure `.env` file has correct keys
5. **Check Ports**: Ensure 3000 and 8000 are available
6. **Review Logs**: Check console output for detailed errors

## 🎉 Success Indicators

### Backend Running Successfully:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Running Successfully:

```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Database Initialized:

- File `resume_system.db` exists in backend directory
- No SQL errors in backend startup logs
- API docs show all endpoints at `/docs`

**🎯 You're ready to go! Visit http://localhost:3000 to use the application.**
