# Start DMR Libertas Backend
# This script starts the backend server directly

# Set environment variables
$env:PYTHONUNBUFFERED = 1
$env:MOCK_MODE = "true"

# Change to backend directory
Set-Location -Path ".\backend"

# Activate virtual environment if it exists
if (Test-Path -Path ".\venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path -Path "..\venv\Scripts\Activate.ps1") {
    & ..\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Please run setup-backend.ps1 first." -ForegroundColor Red
    exit 1
}

# Start the backend server
Write-Host "Starting backend server at http://localhost:8000..." -ForegroundColor Green
uvicorn main:app --reload --host 0.0.0.0 --port 8000
