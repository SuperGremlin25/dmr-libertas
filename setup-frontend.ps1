# Setup script for DMR Libertas frontend
# This script installs dependencies for the frontend

# Change to frontend directory
Set-Location -Path ".\frontend"

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`nFrontend setup complete!" -ForegroundColor Green
Write-Host "To start the frontend server, run: .\start-frontend.ps1" -ForegroundColor Cyan
