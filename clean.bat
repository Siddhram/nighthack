@echo off
echo 🧹 Cleaning up Resume Relevance System...

echo.
echo ⚠️ This will remove all virtual environments and dependencies
echo Press Ctrl+C now if you want to cancel, or
pause

echo.
echo 🧹 Cleaning backend...
cd /d "%~dp0backend"

if exist "venv" (
    echo ✅ Removing virtual environment...
    rmdir /s /q venv
)

if exist "__pycache__" (
    echo ✅ Removing Python cache...
    rmdir /s /q __pycache__
)

if exist "app\__pycache__" (
    echo ✅ Removing app cache...
    rmdir /s /q app\__pycache__
)

cd ..

echo.
echo 🧹 Cleaning frontend...
cd frontend

if exist "node_modules" (
    echo ✅ Removing node_modules...
    rmdir /s /q node_modules
)

if exist "dist" (
    echo ✅ Removing dist...
    rmdir /s /q dist
)

if exist ".vite" (
    echo ✅ Removing Vite cache...
    rmdir /s /q .vite
)

cd ..

echo.
echo ✅ Cleanup completed!
echo Run setup.bat to reinstall everything

pause