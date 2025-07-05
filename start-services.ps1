# DMR Libertas Service Startup Script
# This script ensures all services are properly configured and running

# Set console colors for better readability
$host.UI.RawUI.ForegroundColor = "White"
$host.UI.RawUI.BackgroundColor = "Black"
Clear-Host

Write-Host "===== DMR Libertas Service Startup =====" -ForegroundColor Cyan
Write-Host "Performing pre-flight checks..." -ForegroundColor Yellow

# Check if Docker is running
Write-Host "Checking if Docker is running..." -ForegroundColor Cyan
$dockerRunning = $false
try {
    # Try to get a list of containers as a simple check
    $containerCheck = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerRunning = $true
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker daemon is not responding properly" -ForegroundColor Red
        Write-Host "Docker command returned error code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Try restarting Docker Desktop completely:" -ForegroundColor Yellow
        Write-Host "1. Right-click Docker icon in system tray" -ForegroundColor Yellow
        Write-Host "2. Select 'Quit Docker Desktop'" -ForegroundColor Yellow
        Write-Host "3. Wait a moment, then start Docker Desktop again" -ForegroundColor Yellow
        Write-Host "4. Run this script again once Docker is fully started" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and try again" -ForegroundColor Red
    exit 1
}

# Clean up any existing containers
Write-Host "`nStopping any existing containers..." -ForegroundColor Cyan
docker-compose down

# Remove dangling images
Write-Host "`nCleaning up Docker environment..." -ForegroundColor Cyan
docker system prune -f

# Rebuild and start all services
Write-Host "`nRebuilding and starting all services..." -ForegroundColor Cyan
docker-compose up -d --build

# Wait for services to start
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service status
Write-Host "`nChecking service status:" -ForegroundColor Cyan
docker-compose ps

# Check if backend is running
$backendRunning = $false
$backendContainer = docker ps -qf "name=dmr-libertas_backend"
if ($backendContainer) {
    $backendRunning = $true
    Write-Host "✅ Backend container is running" -ForegroundColor Green
} else {
    Write-Host "❌ Backend container is not running" -ForegroundColor Red
}

# Check if frontend is running
$frontendRunning = $false
$frontendContainer = docker ps -qf "name=dmr-libertas_frontend"
if ($frontendContainer) {
    $frontendRunning = $true
    Write-Host "✅ Frontend container is running" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend container is not running" -ForegroundColor Red
}

# Check if database is running
$dbRunning = $false
$dbContainer = docker ps -qf "name=dmr-libertas_postgres"
if ($dbContainer) {
    $dbRunning = $true
    Write-Host "✅ Database container is running" -ForegroundColor Green
} else {
    Write-Host "❌ Database container is not running" -ForegroundColor Red
}

# Provide service URLs if all services are running
if ($backendRunning -and $frontendRunning -and $dbRunning) {
    Write-Host "`n===== DMR Libertas Services =====" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "Database: PostgreSQL on localhost:5432" -ForegroundColor White
    
    # Try to open the frontend in the default browser
    Write-Host "`nOpening frontend in browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:3000"
    
    Write-Host "`n✅ All services started successfully!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some services failed to start" -ForegroundColor Red
    Write-Host "Please check the logs for more information:" -ForegroundColor Yellow
    Write-Host "docker-compose logs" -ForegroundColor White
}

Write-Host "`nTo view logs in real-time, run:" -ForegroundColor Cyan
Write-Host "docker-compose logs -f" -ForegroundColor White

Write-Host "`nTo stop all services, run:" -ForegroundColor Cyan
Write-Host "docker-compose down" -ForegroundColor White
