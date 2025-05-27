@echo off
echo ======================================================
echo Starting WildFly on Default Ports (8080/9990)
echo ======================================================
echo.

REM Kill any existing Java processes
taskkill /F /IM java.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Navigating to WildFly bin directory...
cd backend\wildfly\wildfly-36.0.0.Final\bin

echo Starting WildFly...
echo.
echo Server will be available at:
echo   - HTTP: http://localhost:8080
echo   - Management: http://localhost:9990
echo.

REM Start WildFly on default ports
start "WildFly Server" cmd /c standalone.bat

echo.
echo WildFly is starting...
echo Please wait 30-60 seconds for startup.
echo.
echo After startup, manually deploy by copying:
echo backend\target\auth-backend.war
echo to:
echo backend\wildfly\wildfly-36.0.0.Final\standalone\deployments\
echo.
echo ======================================================

pause 