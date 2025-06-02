@echo off
echo Configuring PostgreSQL datasource in WildFly...

REM Define WildFly location with absolute path
set WILDFLY_HOME=%~dp0..\wildfly\wildfly-36.0.0.Final
set CLI_SCRIPT=%WILDFLY_HOME%\bin\jboss-cli.bat

REM Check if WildFly exists
if not exist "%WILDFLY_HOME%" (
    echo ERROR: Cannot find WildFly at %WILDFLY_HOME%
    echo Please ensure WildFly is installed correctly.
    exit /b 1
)

REM Check if jboss-cli.bat exists
if not exist "%CLI_SCRIPT%" (
    echo ERROR: Cannot find jboss-cli.bat at %CLI_SCRIPT%
    echo Please ensure WildFly is installed correctly.
    exit /b 1
)

REM Check if WildFly is running
echo Checking if WildFly is running...
jps -l | find "org.jboss.modules.Main" > nul
if %ERRORLEVEL% NEQ 0 (
    echo WildFly is not running. Please start WildFly using scripts\start-wildfly.bat.
    exit /b 1
)

echo WildFly is running. Configuring datasource...

REM Create a temporary CLI script in the current directory
set CLI_COMMANDS=%~dp0datasource-commands.cli
echo batch > "%CLI_COMMANDS%"
echo /subsystem=datasources/jdbc-driver=postgresql:add(driver-name=postgresql,driver-module-name=org.postgresql,driver-class-name=org.postgresql.Driver) >> "%CLI_COMMANDS%"
echo /subsystem=datasources/data-source=AuthDS:add(jndi-name=java:/jdbc/AuthDB,driver-name=postgresql,connection-url=jdbc:postgresql://localhost:5432/authdb,user-name=postgres,password=postgres,min-pool-size=5,max-pool-size=20,enabled=true) >> "%CLI_COMMANDS%"
echo run-batch >> "%CLI_COMMANDS%"

REM Execute the CLI script
call "%CLI_SCRIPT%" --connect --controller=localhost:29990 --file="%CLI_COMMANDS%"

REM Check if the datasource was configured successfully
if %ERRORLEVEL% NEQ 0 (
    echo Failed to configure the datasource. Please check the WildFly logs.
    del "%CLI_COMMANDS%"
    exit /b 1
)

REM Clean up
del "%CLI_COMMANDS%"

echo PostgreSQL datasource configured successfully.
echo You can now deploy your application using Maven: mvn wildfly:deploy 