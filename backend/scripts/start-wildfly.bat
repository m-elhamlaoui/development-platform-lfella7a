@echo off
echo Starting WildFly with port offset 20000...
echo HTTP port: 28081
echo Management port: 29990

REM Define correct path to WildFly
set WILDFLY_HOME=%~dp0..\wildfly\wildfly-36.0.0.Final
set STANDALONE_BAT=%WILDFLY_HOME%\bin\standalone.bat

REM Check if standalone.bat exists
if not exist "%STANDALONE_BAT%" (
    echo ERROR: Cannot find standalone.bat at %STANDALONE_BAT%
    echo Please ensure WildFly is installed correctly.
    exit /b 1
)

REM Start WildFly with a port offset to avoid conflicts
pushd "%WILDFLY_HOME%\bin"
start "WildFly Server" standalone.bat -Djboss.socket.binding.port-offset=20000
popd

echo WildFly starting...
echo Admin console: http://localhost:29990
echo Application: http://localhost:28081/auth-backend

cd ..\..\.. 