@echo off
echo ======================================================
echo Jakarta EE Authentication Backend - Build and Deploy
echo ======================================================
echo.

REM Build the application
echo Building the application...
call mvn clean package
if %ERRORLEVEL% NEQ 0 (
    echo Build failed. Please check the error messages.
    exit /b 1
)
echo.

REM Deploy to WildFly
echo Deploying to WildFly...
call mvn wildfly:deploy
if %ERRORLEVEL% NEQ 0 (
    echo Deployment failed. Ensure WildFly is running.
    echo Try running: scripts\start-wildfly.bat
    exit /b 1
)
echo.

echo ======================================================
echo Deployment completed successfully!
echo.
echo The application is now available at:
echo   http://localhost:28081/auth-backend
echo.
echo API Endpoints:
echo   POST http://localhost:28081/auth-backend/api/auth/signup
echo   POST http://localhost:28081/auth-backend/api/auth/signin
echo ====================================================== 