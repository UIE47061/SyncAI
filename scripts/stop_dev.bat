@echo off
chcp 65001 >nul
REM MBBuddy Local Development Services Stop Script (Windows)

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo.
echo =====================================
echo   Stop MBBuddy Local Development
echo =====================================
echo.

REM Change to project root directory
cd /d "%PROJECT_ROOT%"

echo [INFO] Stopping development services...

REM Stop all uvicorn processes
echo [INFO] Stopping backend services...
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq *uvicorn*" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Backend services stopped
) else (
    echo   No backend services found
)

REM Stop all npm/node processes related to frontend
echo [INFO] Stopping frontend services...
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq *npm*" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Frontend services stopped
) else (
    echo   No frontend services found
)

REM More aggressive cleanup for any remaining processes
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "uvicorn"') do (
    taskkill /f /pid %%i >nul 2>&1
)

for /f "tokens=2" %%i in ('netstat -ano ^| find ":8001"') do (
    taskkill /f /pid %%i >nul 2>&1
)

for /f "tokens=2" %%i in ('netstat -ano ^| find ":5173"') do (
    taskkill /f /pid %%i >nul 2>&1
)

REM Clean up log files (optional)
set /p cleanup="[INFO] Clean up log files? (y/N): "
if /i "%cleanup%"=="y" (
    del /f backend.log >nul 2>&1
    del /f frontend.log >nul 2>&1
    echo   Log files cleaned
)

echo.
echo [SUCCESS] All services stopped
echo.
pause
