@echo off
setlocal
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\cleanup-downloads.ps1" %*
endlocal
