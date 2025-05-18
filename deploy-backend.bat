@echo off
echo ======================================================
echo Jakarta EE Authentication Backend - Deploy Script
echo ======================================================
echo.
echo Running deploy script in the backend folder...
echo.

cd backend
call scripts\deploy.bat
cd ..

echo.
echo ======================================================
echo Deployment completed. The application is now available at:
echo   http://localhost:28081/auth-backend
echo ====================================================== 