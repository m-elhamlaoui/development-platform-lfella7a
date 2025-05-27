@echo off
echo ======================================================
echo Jakarta EE Authentication Backend - Setup Script
echo ======================================================
echo.
echo Running setup script in the backend folder...
echo.

cd backend
call scripts\setup.bat
cd ..

echo.
echo ======================================================
echo Setup completed. You can now deploy the application:
echo   cd backend
echo   scripts\deploy.bat
echo ====================================================== 