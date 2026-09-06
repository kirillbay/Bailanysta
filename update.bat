@echo off
echo ========================================
echo  Bailanysta — Update Launcher
echo ========================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1" %*
echo Exit code: %ERRORLEVEL%
pause
