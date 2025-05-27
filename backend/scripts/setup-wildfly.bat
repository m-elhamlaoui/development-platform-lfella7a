@echo off
echo Setting up WildFly for the authentication backend...

REM Define WildFly location with absolute path
set WILDFLY_HOME=%~dp0..\wildfly\wildfly-36.0.0.Final
set MODULE_DIR=%WILDFLY_HOME%\modules\org\postgresql\main

REM Check if WildFly exists
if not exist "%WILDFLY_HOME%" (
    echo ERROR: Cannot find WildFly at %WILDFLY_HOME%
    echo Please ensure WildFly is installed correctly.
    exit /b 1
)

echo Copying PostgreSQL JDBC driver to WildFly modules...
if not exist "%MODULE_DIR%" mkdir "%MODULE_DIR%"
copy "%~dp0..\lib\postgresql-42.7.2.jar" "%MODULE_DIR%\" /Y

REM Create module.xml if it doesn't exist
echo ^<?xml version="1.0" encoding="UTF-8"?^> > "%MODULE_DIR%\module.xml"
echo ^<module xmlns="urn:jboss:module:1.5" name="org.postgresql"^> >> "%MODULE_DIR%\module.xml"
echo     ^<resources^> >> "%MODULE_DIR%\module.xml"
echo         ^<resource-root path="postgresql-42.7.2.jar"/^> >> "%MODULE_DIR%\module.xml"
echo     ^</resources^> >> "%MODULE_DIR%\module.xml"
echo     ^<dependencies^> >> "%MODULE_DIR%\module.xml"
echo         ^<module name="jakarta.api"/^> >> "%MODULE_DIR%\module.xml"
echo         ^<module name="jakarta.transaction.api"/^> >> "%MODULE_DIR%\module.xml"
echo     ^</dependencies^> >> "%MODULE_DIR%\module.xml"
echo ^</module^> >> "%MODULE_DIR%\module.xml"

echo WildFly setup completed successfully.
echo You can now run start-wildfly.bat to start the server. 