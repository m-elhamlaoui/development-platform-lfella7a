@echo off
echo ======================================================
echo Starting Lost City Backend Server
echo ======================================================
echo.

REM Navigate to backend directory
cd backend

REM Check if WildFly exists
if not exist "wildfly\wildfly-36.0.0.Final\bin\standalone.bat" (
    echo ERROR: WildFly not found or not properly extracted
    echo Please ensure WildFly is properly installed in backend\wildfly\
    pause
    exit /b 1
)

echo Starting WildFly Application Server...
echo.
echo Backend will be available at:
echo   - API: http://localhost:28080/auth-backend
echo   - Management Console: http://localhost:29990
echo.

REM Start WildFly
call scripts\start-wildfly.bat

echo.
echo Backend server startup initiated.
echo Check the WildFly console window for startup progress.
echo ====================================================== 