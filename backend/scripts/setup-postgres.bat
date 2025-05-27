@echo off
echo Setting up PostgreSQL database for the authentication backend...

REM Check if PostgreSQL is installed
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL is not installed or not in PATH.
    echo Please install PostgreSQL and add it to your PATH.
    exit /b 1
)

REM Create the database
echo Creating authdb database...
psql -U postgres -c "DROP DATABASE IF EXISTS authdb;"
psql -U postgres -c "CREATE DATABASE authdb WITH ENCODING 'UTF8';"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to create the database.
    echo Please check your PostgreSQL installation and credentials.
    exit /b 1
)

echo Database created successfully.
echo You can now configure the WildFly datasource by running setup-wildfly.bat.

REM Define correct path to WildFly
set WILDFLY_HOME=%~dp0..\wildfly\wildfly-36.0.0.Final
set JBOSS_CLI=%WILDFLY_HOME%\bin\jboss-cli.bat

REM Check if jboss-cli.bat exists
if not exist "%JBOSS_CLI%" (
    echo WARNING: Cannot find jboss-cli.bat at %JBOSS_CLI%
    echo Skipping PostgreSQL driver configuration in WildFly.
    exit /b 0
)

REM Execute PostgreSQL configuration script using JBoss CLI
echo Configuring PostgreSQL driver in WildFly...
call "%JBOSS_CLI%" --file="%~dp0..\config\configure-postgres.cli"

echo PostgreSQL setup completed successfully. 