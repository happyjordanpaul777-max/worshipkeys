@echo off
setlocal
cd /d "%~dp0"
title WorshipKeys Local Songbook

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11 or newer from https://www.python.org/downloads/
  echo During installation, enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo First-time setup: a private .env file has been created.
  echo Open .env in Notepad and replace the DATABASE_URL placeholder
  echo with the EXTERNAL PostgreSQL URL from Render > Database > Connect.
  echo LOCAL_SHARED_MODE should remain true.
  echo Do not share .env or upload it to GitHub.
  echo.
  start notepad ".env"
  pause
  exit /b 0
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating the local Python environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Could not create the Python environment.
    pause
    exit /b 1
  )
)

echo Installing or updating WorshipKeys requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)

echo.
echo Starting WorshipKeys at http://127.0.0.1:8000
echo Keep this window open while using WorshipKeys.
start "" http://127.0.0.1:8000
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
