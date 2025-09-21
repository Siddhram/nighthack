@echo off
echo 🔧 Setting up Resume Relevance System...

REM Colors simulation for Windows
REM GREEN = ✅, YELLOW = ⚠️, RED = ❌

echo.
echo 📋 Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% found

echo.
echo 🔧 Setting up Backend...
cd /d "%~dp0backend"

REM Create virtual environment
if not exist "venv" (
    echo ✅ Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ✅ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo ✅ Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Create .env file
if not exist ".env" (
    echo ✅ Creating .env file...
    copy .env.example .env >nul
    echo ⚠️ Please edit backend\.env and configure your API keys
)

REM Create uploads directory
if not exist "uploads" (
    echo ✅ Creating uploads directory...
    mkdir uploads
)

REM Initialize database
echo ✅ Initializing database...
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database tables created successfully')"
if %errorlevel% neq 0 (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)

cd ..

echo.
echo 🎨 Setting up Frontend...
cd frontend

REM Install Node.js dependencies
echo ✅ Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

cd ..

echo.
echo ✅ Setup completed successfully!
echo.
echo 📝 Next steps:
echo 1. Edit backend\.env and add your API keys
echo 2. Run start-backend.bat to start the backend server
echo 3. Run start-frontend.bat to start the frontend server
echo 4. Open http://localhost:3000 in your browser
echo.
echo 🔗 API Documentation will be available at: http://localhost:8000/docs
echo.
echo ⚠️ Make sure to set your API keys in backend\.env before starting!

pause