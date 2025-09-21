@echo off
echo 🚀 Starting Complete Resume Relevance System...

REM Start backend in new window
echo ✅ Starting Backend Server...
start "Resume Backend" /d "%~dp0" cmd /c "start-backend.bat"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window  
echo ✅ Starting Frontend Server...
start "Resume Frontend" /d "%~dp0" cmd /c "start-frontend.bat"

echo.
echo 🎉 Both servers are starting...
echo.
echo 🌐 Frontend: http://localhost:3000
echo 📡 Backend: http://localhost:8000  
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo ⚠️ Both servers will open in separate windows
echo Close those windows to stop the servers
echo.

pause