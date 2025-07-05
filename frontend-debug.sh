#!/bin/bash
# Frontend Debug Script for DMR Libertas

echo "==== DMR Libertas Frontend Debug Script ===="
echo "Checking Docker container status..."
docker ps -a

echo -e "\n==== Checking frontend container logs ===="
docker-compose logs frontend

echo -e "\n==== Checking frontend container network ===="
FRONTEND_CONTAINER=$(docker ps -qf "name=dmr-libertas_frontend")
if [ -z "$FRONTEND_CONTAINER" ]; then
  echo "Frontend container is not running!"
else
  echo "Frontend container ID: $FRONTEND_CONTAINER"
  echo "Container network settings:"
  docker inspect --format='{{json .NetworkSettings.Networks}}' $FRONTEND_CONTAINER | jq
  
  echo -e "\n==== Testing frontend container connectivity ===="
  docker exec $FRONTEND_CONTAINER curl -s http://localhost:3000 > /dev/null
  if [ $? -eq 0 ]; then
    echo "✅ Frontend is accessible within the container"
  else
    echo "❌ Frontend is NOT accessible within the container"
  fi
  
  echo -e "\n==== Checking backend connectivity from frontend ===="
  docker exec $FRONTEND_CONTAINER curl -s http://backend:8000/docs > /dev/null
  if [ $? -eq 0 ]; then
    echo "✅ Backend is accessible from frontend container"
  else
    echo "❌ Backend is NOT accessible from frontend container"
  fi
fi

echo -e "\n==== Checking frontend build ===="
docker-compose exec frontend ls -la /app/.next || echo "Cannot access .next directory - build may have failed"

echo -e "\n==== Checking frontend environment variables ===="
docker-compose exec frontend env | grep NEXT

echo -e "\n==== Recommendations ===="
echo "1. If frontend container is not running, try: docker-compose up -d frontend"
echo "2. If build failed, check for errors in: docker-compose logs frontend"
echo "3. If network issues, verify environment variables in docker-compose.yml"
echo "4. Try rebuilding frontend: docker-compose build --no-cache frontend"
echo "5. For Windows users, ensure Docker Desktop is properly configured for networking"
