# Setup script for DMR Libertas backend
# This script sets up the Python environment and installs dependencies

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

Write-Host "`nBackend setup complete!" -ForegroundColor Green
Write-Host "To start the backend server, run: .\start-backend.ps1" -ForegroundColor Cyan
