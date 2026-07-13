@echo off
REM MSME Financial Health Score - Setup Script for Windows
REM This script helps set up the development environment

echo ================================================
echo MSME Financial Health Score - Setup Script
echo ================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python not found. Please install Python 3.9+
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo + Found %PYTHON_VERSION%

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Node.js not found. Please install Node.js 18+
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo + Found Node.js %NODE_VERSION%

echo.
echo ================================================
echo Setting up Backend...
echo ================================================

cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo + Virtual environment created
) else (
    echo + Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo + Python dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ! Please edit backend\.env with your Supabase credentials
) else (
    echo + .env file already exists
)

cd ..

echo.
echo ================================================
echo Setting up Frontend...
echo ================================================

cd frontend

REM Install Node dependencies
echo Installing Node.js dependencies...
call npm install
echo + Node.js dependencies installed

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ! Please edit frontend\.env with your Supabase credentials
) else (
    echo + .env file already exists
)

cd ..

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Set up your Supabase project:
echo    - Go to https://app.supabase.com/
echo    - Create a new project
echo    - Enable Email/Password authentication
echo    - Copy your credentials from Project Settings -^> API
echo.
echo 2. Configure environment variables:
echo    - Edit backend\.env with your Supabase credentials
echo    - Edit frontend\.env with your Supabase credentials
echo.
echo 3. Start the backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python app.py
echo.
echo 4. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 5. Open http://localhost:3000 in your browser
echo.
echo For detailed instructions, see README.md
echo.

pause
