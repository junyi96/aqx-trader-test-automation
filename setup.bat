@echo off
REM Setup script for AQX Trader Test Automation Framework (Windows)

echo ==========================================
echo AQX Trader Test Automation Framework Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv
echo Virtual environment created!
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed!
echo.

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install
echo Browsers installed!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo .env file created! Please edit it with your credentials.
) else (
    echo .env file already exists.
)
echo.

REM Create necessary directories
echo Creating directories...
if not exist reports mkdir reports
if not exist screenshots mkdir screenshots
if not exist traces mkdir traces
if not exist logs mkdir logs
echo Directories created!
echo.

echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: .venv\Scripts\activate
echo 3. Run tests: pytest
echo.
echo For more information, see README_NEW.md

pause