@echo off
setlocal

REM Move to the project root relative to this script.
cd /d "%~dp0.."

set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERROR: Project virtual environment not found.
    echo Expected: %PYTHON_EXE%
    echo.
    echo Create it with:
    echo python -m venv .venv
    exit /b 1
)

echo ============================================================
echo Job Match Agent - Market Intelligence Refresh
echo ============================================================
echo Project: %CD%
echo.

"%PYTHON_EXE%" -m scripts.refresh_market_once

set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo ERROR: Market refresh failed with exit code %EXIT_CODE%.
)

exit /b %EXIT_CODE%
