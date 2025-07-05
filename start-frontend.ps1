# Start DMR Libertas Frontend
# This script starts the frontend development server directly

# Set environment variables
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_WS_URL = "ws://localhost:8000/ws"
$env:NEXT_TELEMETRY_DISABLED = 1

# Change to frontend directory
Set-Location -Path ".\frontend"

# Start the frontend server
Write-Host "Starting frontend server at http://localhost:3000..." -ForegroundColor Green
npm run dev
