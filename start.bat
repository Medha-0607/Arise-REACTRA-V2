@echo off
title REACTRA V2 — Field Testing Launcher
color 0A

echo ===============================================================================
echo   REACTRA V2 — Reaction-Aware Field Testing ^& Verifiable Evidence
echo   Smart India Hackathon (SIH 2026) — Team ARISE (SIH26231)
echo ===============================================================================
echo.

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: 1. Check Python Availability
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python 3 is not installed or not added to PATH.
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

:: 2. Check Node.js / NPM Availability
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js / npm is not installed or not added to PATH.
    echo Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

:: 3. Launch Backend Service (FastAPI)
echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "REACTRA V2 - Backend Service" cmd /k "cd /d ""%ROOT_DIR%backend"" && (if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat else if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat) && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 4. Launch Frontend Service (Vite + React)
echo [2/3] Starting Vite Frontend on http://localhost:5173 ...
start "REACTRA V2 - Frontend UI" cmd /k "cd /d ""%ROOT_DIR%frontend"" && npm run dev"

:: 5. Wait for servers to initialize
echo [3/3] Initializing services and opening web application in browser...
timeout /t 3 /nobreak >nul

:: 6. Open Browser
start http://localhost:5173/home

echo.
echo ===============================================================================
echo   SERVICES RUNNING SUCCESSFULLY:
echo   - Web Application:       http://localhost:5173/home
echo   - Backend REST API:      http://127.0.0.1:8000
echo   - Interactive API Docs:  http://127.0.0.1:8000/docs
echo   - API Specification:     http://127.0.0.1:8000/redoc
echo ===============================================================================
echo   To stop all services, simply close the backend and frontend terminal windows.
echo.
pause
