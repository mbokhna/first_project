@echo off
cd /d "%~dp0\.."

docker build -t pm-app .
docker rm -f pm-app >nul 2>&1
docker run -d --name pm-app -p 8000:8000 --env-file .env pm-app

echo App running at http://localhost:8000
