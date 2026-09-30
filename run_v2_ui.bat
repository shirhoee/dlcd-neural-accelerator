@echo off
echo ==================================================
echo   Starting V2 DLCD Neural Accelerator Dashboard
echo ==================================================

echo.
echo Starting FastAPI Backend...
cd v2\v2_ui\backend
start "DLCD Backend (FastAPI)" cmd /k "python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo Starting React Frontend...
cd ..\frontend
start "DLCD Frontend (Vite)" cmd /k "npm run dev"

cd ..\..\..
echo.
echo Services have been launched in separate windows!
echo - Backend is running on http://127.0.0.1:8000
echo - Frontend is running on http://localhost:5173
echo.
pause
