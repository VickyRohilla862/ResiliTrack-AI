@echo off
REM ResiliTrack AI - Windows Quick Start Script

echo.
echo ========================================
echo ResiliTrack AI - Quick Start (Windows)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Setting up Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo WARNING: Please edit backend\.env and add your GEMINI_API_KEY
)

cd ..

echo.
echo [2/4] Setting up Frontend...
cd frontend
npm run build

if not exist node_modules (
    echo Installing Node.js packages...
    call npm install
)

cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo.
echo Open your terminal and run the following commands:
echo   cd backend
echo   venv\Scripts\activate
echo   python app.py
echo.
echo Then open your browser to:
echo   http://localhost:5173
echo.
pause
