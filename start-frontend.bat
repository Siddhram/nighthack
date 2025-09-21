@echo off
echo 🎨 Starting Resume Relevance System Frontend...

REM Navigate to frontend directory
cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo ❌ Node modules not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo ✅ Starting Vite development server...
echo 🌐 Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev