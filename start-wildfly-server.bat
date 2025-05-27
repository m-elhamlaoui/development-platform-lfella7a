@echo off
echo ======================================================
echo Starting WildFly Application Server for Lost City App
echo ======================================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%
set BACKEND_DIR=%PROJECT_ROOT%backend
set WILDFLY_HOME=%BACKEND_DIR%\wildfly\wildfly-36.0.0.Final
set WILDFLY_BIN=%WILDFLY_HOME%\bin

echo Script directory: %SCRIPT_DIR%
echo Backend directory: %BACKEND_DIR%
echo WildFly home: %WILDFLY_HOME%
echo.

REM Check if WildFly exists
if not exist "%WILDFLY_BIN%\standalone.bat" (
    echo ERROR: WildFly standalone.bat not found at %WILDFLY_BIN%\standalone.bat
    echo Please ensure WildFly is properly extracted in the backend\wildfly directory.
    pause
    exit /b 1
)

echo Found WildFly installation at: %WILDFLY_HOME%
echo.

REM Kill any existing Java processes
echo Stopping any existing Java processes...
taskkill /F /IM java.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting WildFly with port offset...
echo.
echo Server will be available at:
echo   - HTTP: http://localhost:28081
echo   - Management: http://localhost:29990
echo   - Application: http://localhost:28081/auth-backend
echo.

REM Change to WildFly bin directory
cd /d "%WILDFLY_BIN%"

REM Start WildFly with port offset
echo Executing: standalone.bat -Djboss.socket.binding.port-offset=20000
echo.
start "WildFly Server - Lost City App" standalone.bat -Djboss.socket.binding.port-offset=20000

echo.
echo WildFly is starting in a new window...
echo Please wait 30-60 seconds for the server to fully start.
echo.

REM Wait a bit and then deploy the application
echo Waiting 30 seconds for server startup...
timeout /t 30 /nobreak

echo.
echo Deploying application...
cd /d "%BACKEND_DIR%"

if exist "target\auth-backend.war" (
    echo Copying WAR file to deployments directory...
    copy "target\auth-backend.war" "%WILDFLY_HOME%\standalone\deployments\" >nul
    echo Application deployed successfully!
) else (
    echo WARNING: WAR file not found. You may need to build the application first.
    echo Run: mvn clean package
)

echo.
echo ======================================================
echo Backend server startup complete!
echo.
echo Access your application at:
echo   http://localhost:28081/auth-backend
echo.
echo Management console at:
echo   http://localhost:29990
echo ======================================================
pause 