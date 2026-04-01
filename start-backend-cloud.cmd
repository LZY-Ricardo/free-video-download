@echo off
setlocal
cd /d "%~dp0backend"
powershell -ExecutionPolicy Bypass -File ".\start-cloud.ps1" %*
endlocal
