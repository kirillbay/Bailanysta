@echo off
REM Bailanysta — Launcher for install.ps1
REM Ensures PowerShell runs with correct policy and shows output

echo ========================================
echo  Bailanysta — Installer Launcher
echo ========================================
echo.

REM Check PowerShell available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERR] PowerShell not found. Install PowerShell 5.1+ or PowerShell 7.
    pause
    exit /b 1
)

REM Run installer with Bypass to allow script execution
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*

echo.
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Installer finished with errors — check log above.
) else (
    echo [OK] Installer finished.
)
pause
