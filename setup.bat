@echo off
echo ==================================
echo Slack-CATestDriveApp Setup Script
echo ==================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8-3.13 from python.org
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

REM Check for Python 3.14
python -c "import sys; exit(0 if sys.version_info.major == 3 and sys.version_info.minor < 14 else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: You are using Python 3.14 or later!
    echo This may cause issues with pyodbc installation.
    echo.
    echo Recommended solutions:
    echo   1. Install Python 3.13 from python.org
    echo   2. Use pre-built wheel: pip install --only-binary :all: pyodbc
    echo.
    pause
)

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies
    echo.
    echo If you're having issues with pyodbc, try:
    echo   pip install --only-binary :all: pyodbc
    echo   pip install slack-bolt slack-sdk python-dotenv requests
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!

REM Check for .env file
echo.
if exist .env (
    echo .env file found
) else (
    echo .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your Slack tokens:
    echo   - SLACK_BOT_TOKEN ^(starts with xoxb-^)
    echo   - SLACK_APP_TOKEN ^(starts with xapp-^)
)

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env and add your Slack tokens
echo 2. Run the app: python app.py
echo.
echo For detailed instructions, see README.md
echo For troubleshooting, see TROUBLESHOOTING.md
echo.
pause
