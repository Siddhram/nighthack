@echo off
echo Starting Resume Relevance System...
echo.

echo Starting Backend Server...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "python -c \"import sys; sys.path.insert(0, '.'); import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000)\""

timeout /t 3 /nobreak

echo Starting Frontend Server...
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window (servers will keep running)
pause