# Run DMR Libertas locally without Docker
# This script runs the backend and frontend directly on your machine

Write-Host "===== DMR Libertas Local Development =====" -ForegroundColor Cyan

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check Node.js installation
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Setup backend
Write-Host "`nSetting up backend..." -ForegroundColor Cyan
Set-Location -Path ".\backend"

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path ".\venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Set environment variables for backend
$env:PYTHONUNBUFFERED = 1
$env:MOCK_MODE = "true"

# Start backend in a new window
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; & .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# Setup frontend
Write-Host "`nSetting up frontend..." -ForegroundColor Cyan
Set-Location -Path "..\frontend"

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
npm install

# Set environment variables for frontend
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_WS_URL = "ws://localhost:8000/ws"
$env:NEXT_TELEMETRY_DISABLED = 1

# Start frontend in a new window
Write-Host "Starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; npm run dev"

# Return to project root
Set-Location -Path ".."

Write-Host "`n===== Services Started =====" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor White

# Try to open the frontend in the default browser
Write-Host "`nOpening frontend in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"
