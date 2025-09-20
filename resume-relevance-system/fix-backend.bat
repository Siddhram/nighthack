@echo off
echo 🔧 Quick Backend Fix - Starting with Dashboard API
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Running setup...
    cd ..
    call setup.bat
    cd backend
)

echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

echo ✅ Installing/updating dependencies...
pip install -r requirements.txt

echo ✅ Creating .env file if needed...
if not exist ".env" (
    copy .env.example .env
)

echo ✅ Initializing database...
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database ready!')"

echo ✅ Starting FastAPI server with Dashboard API...
echo 📡 Backend will be available at: http://localhost:8000
echo 📚 API Documentation at: http://localhost:8000/docs
echo 🎯 Dashboard Stats API: http://localhost:8000/api/dashboard/stats
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause