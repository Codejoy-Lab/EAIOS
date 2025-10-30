@echo off
echo Stopping old backend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing PID %%a
    taskkill /F /PID %%a 2>nul
)

echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo Starting new backend...
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
