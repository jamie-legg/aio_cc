@echo off
echo Content Creation Tool - Windows Setup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv package manager...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install uv
        echo Please install manually from https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
)

REM Install project dependencies
echo Installing project dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo Please install FFmpeg using one of these methods:
    echo 1. Using Chocolatey: choco install ffmpeg
    echo 2. Using winget: winget install ffmpeg
    echo 3. Manual installation from https://ffmpeg.org/download.html
    echo.
    echo After installation, restart this script.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your API credentials
    echo You can open it with: notepad .env
    echo.
)

REM Set up default directories
echo Setting up default directories...
uv run content-cli config set-watch-dir "%USERPROFILE%\Videos"
uv run content-cli config set-processed-dir "%USERPROFILE%\Videos\Processed"

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your API credentials
echo 2. Run: uv run content-cli auth all
echo 3. Run: uv run python main.py
echo.
pause
