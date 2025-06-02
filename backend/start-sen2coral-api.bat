@echo off
echo Starting Sen2Coral API Server...
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r sen2coral_api/requirements.txt

echo.
echo Starting FastAPI server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

cd sen2coral_api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause 