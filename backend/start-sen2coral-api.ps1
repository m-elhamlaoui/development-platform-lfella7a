#!/usr/bin/env pwsh

Write-Host "🌊 Starting Sen2Coral API Server..." -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r sen2coral_api/requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Green
Write-Host "📍 Server: http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "🏥 Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "🔧 Capabilities: http://localhost:8000/api/sen2coral/capabilities" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

Set-Location sen2coral_api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload 