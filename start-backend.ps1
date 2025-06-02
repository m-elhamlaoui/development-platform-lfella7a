Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Starting Lost City Backend Server" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location backend

# Check if WildFly exists
if (-not (Test-Path "wildfly\wildfly-36.0.0.Final\bin\standalone.bat")) {
    Write-Host "ERROR: WildFly not found or not properly extracted" -ForegroundColor Red
    Write-Host "Please ensure WildFly is properly installed in backend\wildfly\" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting WildFly Application Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Yellow
Write-Host "  - API: http://localhost:28080/auth-backend" -ForegroundColor White
Write-Host "  - Management Console: http://localhost:29990" -ForegroundColor White
Write-Host ""

# Start WildFly
try {
    & "scripts\start-wildfly.bat"
    Write-Host ""
    Write-Host "Backend server startup initiated." -ForegroundColor Green
    Write-Host "Check the WildFly console window for startup progress." -ForegroundColor Yellow
} catch {
    Write-Host "Error starting WildFly: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "======================================================" -ForegroundColor Cyan 