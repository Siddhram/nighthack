# 🔧 Troubleshooting Guide

## 🚨 Common Issues & Quick Fixes

### 1. **PowerShell Execution Policy Error**

```
.\setup.ps1 : cannot be loaded because running scripts is disabled on this system
```

**Fix:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. **Virtual Environment Activation Fails**

```
.\venv\Scripts\activate : cannot be loaded because running scripts is disabled
```

**Fix:**

```powershell
# Option 1: Change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Option 2: Use batch file instead
venv\Scripts\activate.bat
```

### 3. **Module Import Errors**

```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:**

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt
```

### 4. **Port Already in Use**

```
OSError: [WinError 10048] Only one usage of each socket address is normally permitted
```

**Fix:**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace 1234 with actual PID)
taskkill /PID 1234 /F

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

### 5. **Database Connection Error**

```
sqlite3.OperationalError: no such table: jobs
```

**Fix:**

```powershell
cd backend
.\venv\Scripts\activate

# Reinitialize database
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database recreated')"
```

### 6. **API Key Configuration Issues**

```
Error: PINECONE_API_KEY not found
```

**Fix:**

1. Open `backend\.env` file
2. Ensure API keys are set:

```bash
PINECONE_API_KEY=pcsk_4B27To_tY2jeLoxqgm97GKUfwxMccU39ZsN3jcd2D8Lq7UjZhjwEyHerwKDc8hpeinqpe
GEMINI_API_KEY=your_actual_key_here
```

### 7. **Frontend Build Errors**

```
npm ERR! code ENOENT
```

**Fix:**

```powershell
cd frontend

# Clear npm cache
npm cache clean --force

# Remove and reinstall
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install
```

### 8. **CORS Errors in Browser**

```
Access to XMLHttpRequest blocked by CORS policy
```

**Fix:**
Check `backend\.env` has correct CORS settings:

```bash
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### 9. **File Upload Errors**

```
413 Request Entity Too Large
```

**Fix:**
Check file size limits in `backend\.env`:

```bash
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

### 10. **Dependency Version Conflicts**

```
ERROR: pip's dependency resolver does not currently have a backtracking strategy
```

**Fix:**

```powershell
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Or create new virtual environment
Remove-Item venv -Recurse -Force
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 🔍 Diagnostic Commands

### Check System Status:

```powershell
# Check if virtual environment is active
echo $env:VIRTUAL_ENV

# Check Python version
python --version

# Check installed packages
pip list

# Check running processes on ports
netstat -ano | findstr ":8000"
netstat -ano | findstr ":3000"
```

### Test Backend:

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test with PowerShell
Invoke-RestMethod -Uri http://localhost:8000/health
```

### Test Database:

```powershell
cd backend
.\venv\Scripts\activate

python -c "
from app.models.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT name FROM sqlite_master WHERE type=\"table\";'))
    tables = [row[0] for row in result]
    print(f'Tables: {tables}')
"
```

## 🛠️ Reset Everything

### Nuclear Option - Complete Reset:

```powershell
# Stop all servers (Ctrl+C in their terminals)

# Clean everything
.\clean.bat

# Or manually:
Remove-Item backend\venv -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item frontend\node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backend\resume_system.db -ErrorAction SilentlyContinue

# Reinstall everything
.\setup.bat
```

## 📞 Getting Help

### Check Logs:

1. **Backend Logs**: Look at terminal where uvicorn is running
2. **Frontend Logs**: Look at terminal where npm run dev is running
3. **Browser Console**: F12 → Console tab for frontend errors

### Verify Installation:

```powershell
# Backend check
cd backend
.\venv\Scripts\activate
python -c "import fastapi, uvicorn, sqlalchemy; print('Backend dependencies OK')"

# Frontend check
cd frontend
npm list --depth=0
```

### Environment Check:

```powershell
# Show all environment variables
cd backend
Get-Content .env

# Test API keys (don't share output!)
python -c "
from app.config import settings
print(f'Pinecone configured: {bool(settings.pinecone_api_key)}')
print(f'Gemini configured: {bool(settings.gemini_api_key)}')
"
```

## 🎯 Success Indicators

### ✅ Everything Working:

- Backend shows: `Application startup complete.`
- Frontend shows: `ready in XXX ms`
- Browser loads http://localhost:3000 without errors
- API docs accessible at http://localhost:8000/docs
- No error messages in terminals

### ❌ Something's Wrong:

- Error messages in terminal
- Browser shows "This site can't be reached"
- API docs show 404 or connection error
- Import errors when starting servers

Remember: **Most issues are solved by ensuring the virtual environment is activated and all dependencies are properly installed!**
