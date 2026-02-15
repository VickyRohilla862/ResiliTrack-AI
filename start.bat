@echo off
REM ResiliTrack AI - Start Backend and Frontend (Windows)

echo.
echo ========================================
echo ResiliTrack AI - Startup Script
echo ========================================
echo.

REM Start Backend
echo Starting ResiliTrack AI on Port 5000...
echo.
cd backend
call venv\Scripts\activate.bat
start "ResiliTrack AI - Backend" python app.py

REM Wait a moment
timeout /t 2

REM Start Frontend
echo Starting Frontend on Port 5173...
echo.
cd ..\frontend
start "ResiliTrack AI - Frontend" cmd /k npm run dev

cd ..

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
@REM echo Frontend:  http://localhost:5173
echo ResiliTrack AI :   http://localhost:5000
echo.
echo Close either terminal command window to stop that service.
echo Press any key to exit this script...
echo.
pause
