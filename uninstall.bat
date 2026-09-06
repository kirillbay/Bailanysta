@echo off
echo ========================================
echo  Bailanysta — Uninstall Launcher
echo ========================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" %*
echo Exit code: %ERRORLEVEL%
pause
