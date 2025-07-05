# Frontend Debug Script for DMR Libertas (PowerShell version)

Write-Host "==== DMR Libertas Frontend Debug Script ====" -ForegroundColor Cyan
Write-Host "Checking Docker container status..." -ForegroundColor Cyan
docker ps -a

Write-Host "`n==== Checking frontend container logs ====" -ForegroundColor Cyan
docker-compose logs frontend

Write-Host "`n==== Checking frontend container network ====" -ForegroundColor Cyan
$FRONTEND_CONTAINER = docker ps -qf "name=dmr-libertas_frontend"
if (-not $FRONTEND_CONTAINER) {
  Write-Host "Frontend container is not running!" -ForegroundColor Red
} else {
  Write-Host "Frontend container ID: $FRONTEND_CONTAINER" -ForegroundColor Green
  Write-Host "Container network settings:" -ForegroundColor Cyan
  docker inspect --format='{{json .NetworkSettings.Networks}}' $FRONTEND_CONTAINER
  
  Write-Host "`n==== Testing frontend container connectivity ====" -ForegroundColor Cyan
  $result = docker exec $FRONTEND_CONTAINER curl -s http://localhost:3000
  if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend is accessible within the container" -ForegroundColor Green
  } else {
    Write-Host "❌ Frontend is NOT accessible within the container" -ForegroundColor Red
  }
  
  Write-Host "`n==== Checking backend connectivity from frontend ====" -ForegroundColor Cyan
  $result = docker exec $FRONTEND_CONTAINER curl -s http://backend:8000/docs
  if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend is accessible from frontend container" -ForegroundColor Green
  } else {
    Write-Host "❌ Backend is NOT accessible from frontend container" -ForegroundColor Red
  }
}

Write-Host "`n==== Checking frontend build ====" -ForegroundColor Cyan
docker-compose exec frontend ls -la /app/.next 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Cannot access .next directory - build may have failed" -ForegroundColor Red
}

Write-Host "`n==== Checking frontend environment variables ====" -ForegroundColor Cyan
docker-compose exec frontend env | Select-String "NEXT"

Write-Host "`n==== Recommendations ====" -ForegroundColor Yellow
Write-Host "1. If frontend container is not running, try: docker-compose up -d frontend" -ForegroundColor White
Write-Host "2. If build failed, check for errors in: docker-compose logs frontend" -ForegroundColor White
Write-Host "3. If network issues, verify environment variables in docker-compose.yml" -ForegroundColor White
Write-Host "4. Try rebuilding frontend: docker-compose build --no-cache frontend" -ForegroundColor White
Write-Host "5. For Windows users, ensure Docker Desktop is properly configured for networking" -ForegroundColor White
Write-Host "6. Check Windows Firewall settings to ensure ports 3000 and 8000 are allowed" -ForegroundColor White
