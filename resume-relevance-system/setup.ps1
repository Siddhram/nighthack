# Resume Relevance System - PowerShell Setup Script
param(
    [switch]$Force,
    [switch]$Clean
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = "White"

function Write-Status {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

Write-Host "🚀 Resume Relevance System Setup" -ForegroundColor Magenta
Write-Host "=================================" -ForegroundColor Magenta
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "README.md")) {
    Write-Error "Please run this script from the project root directory"
    exit 1
}

Write-Status "Checking system requirements..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Status "Python found: $pythonVersion"
    
    # Check Python version
    $version = [System.Version]($pythonVersion -replace "Python ", "")
    if ($version -lt [System.Version]"3.9.0") {
        Write-Error "Python 3.9+ required. Found: $pythonVersion"
        exit 1
    }
} catch {
    Write-Error "Python 3.9+ is required but not found"
    Write-Info "Download from: https://python.org/downloads/"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Status "Node.js found: $nodeVersion"
    
    # Check Node.js version
    $version = [int]($nodeVersion -replace "v(\d+)\..*", '$1')
    if ($version -lt 18) {
        Write-Error "Node.js 18+ required. Found: $nodeVersion"
        exit 1
    }
} catch {
    Write-Error "Node.js 18+ is required but not found"
    Write-Info "Download from: https://nodejs.org/"
    exit 1
}

Write-Host ""
Write-Status "Setting up Backend..."

# Navigate to backend
Push-Location "backend"

try {
    # Create virtual environment
    if (-not (Test-Path "venv") -or $Force) {
        if ($Force -and (Test-Path "venv")) {
            Write-Status "Removing existing virtual environment..."
            Remove-Item -Recurse -Force "venv"
        }
        Write-Status "Creating Python virtual environment..."
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
    }
    
    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install dependencies
    Write-Status "Installing Python dependencies..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    
    # Create .env file
    if (-not (Test-Path ".env")) {
        Write-Status "Creating .env file..."
        Copy-Item ".env.example" ".env"
        Write-Warning "Please edit backend\.env and configure your API keys!"
    }
    
    # Create uploads directory
    if (-not (Test-Path "uploads")) {
        Write-Status "Creating uploads directory..."
        New-Item -ItemType Directory "uploads" | Out-Null
    }
    
    # Initialize database
    Write-Status "Initializing database..."
    python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database initialized successfully')"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to initialize database"
    }
    
} catch {
    Write-Error "Backend setup failed: $_"
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

Write-Host ""
Write-Status "Setting up Frontend..."

# Navigate to frontend
Push-Location "frontend"

try {
    # Install Node.js dependencies
    Write-Status "Installing Node.js dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Node.js dependencies"
    }
    
} catch {
    Write-Error "Frontend setup failed: $_"
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

Write-Host ""
Write-Status "Setup completed successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend\.env and add your API keys"
Write-Host "2. Run backend: .\start-backend.bat or use PowerShell"
Write-Host "3. Run frontend: .\start-frontend.bat or use PowerShell" 
Write-Host "4. Open http://localhost:3000 in your browser"
Write-Host ""

Write-Host "🔗 URLs:" -ForegroundColor Cyan
Write-Host "Frontend:  http://localhost:3000"
Write-Host "Backend:   http://localhost:8000"
Write-Host "API Docs:  http://localhost:8000/docs"
Write-Host ""

Write-Warning "Don't forget to configure your API keys in backend\.env!"

# Quick commands
Write-Host ""
Write-Host "💡 Quick Commands:" -ForegroundColor Magenta
Write-Host ".\setup.ps1 -Force     # Force reinstall everything"
Write-Host ".\setup.ps1 -Clean     # Clean and reinstall"
Write-Host ".\start-all.bat        # Start both servers"