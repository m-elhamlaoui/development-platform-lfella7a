@echo off
echo ======================================================
echo Jakarta EE Authentication Backend - Setup Script
echo ======================================================
echo.
echo This script will set up the entire environment:
echo 1. Create PostgreSQL database
echo 2. Configure WildFly
echo 3. Start WildFly server
echo 4. Configure the datasource
echo.
echo ======================================================

REM Setup PostgreSQL
echo Step 1: Setting up PostgreSQL database...
call scripts\setup-postgres.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to set up PostgreSQL. Aborting.
    exit /b 1
)
echo.

REM Setup WildFly
echo Step 2: Setting up WildFly...
call scripts\setup-wildfly.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to set up WildFly. Aborting.
    exit /b 1
)
echo.

REM Start WildFly
echo Step 3: Starting WildFly server...
start "WildFly" /B cmd /c scripts\start-wildfly.bat
echo Waiting for WildFly to start...
timeout /t 15 /nobreak
echo.

REM Configure datasource
echo Step 4: Configuring the datasource...
call scripts\configure-datasource.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to configure datasource. Please check the logs.
    exit /b 1
)
echo.

echo ======================================================
echo Setup completed successfully!
echo.
echo You can now build and deploy the application:
echo   mvn clean package wildfly:deploy
echo.
echo Access the application at:
echo   http://localhost:28081/auth-backend
echo ====================================================== 