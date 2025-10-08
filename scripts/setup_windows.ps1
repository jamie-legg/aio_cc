# Content Creation Tool - Windows PowerShell Setup
Write-Host "Content Creation Tool - Windows Setup" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if uv is installed
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✓ uv found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing uv package manager..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile "install_uv.ps1"
        & ".\install_uv.ps1"
        Remove-Item "install_uv.ps1" -ErrorAction SilentlyContinue
        Write-Host "✓ uv installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ ERROR: Failed to install uv" -ForegroundColor Red
        Write-Host "Please install manually from https://github.com/astral-sh/uv" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Install project dependencies
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
try {
    uv sync
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if FFmpeg is installed
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg found: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ WARNING: FFmpeg is not installed or not in PATH" -ForegroundColor Yellow
    Write-Host "Please install FFmpeg using one of these methods:" -ForegroundColor Yellow
    Write-Host "1. Using Chocolatey: choco install ffmpeg" -ForegroundColor Cyan
    Write-Host "2. Using winget: winget install ffmpeg" -ForegroundColor Cyan
    Write-Host "3. Manual installation from https://ffmpeg.org/download.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, restart this script." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env file with your API credentials" -ForegroundColor Red
    Write-Host "You can open it with: notepad .env" -ForegroundColor Cyan
    Write-Host ""
}

# Set up default directories
Write-Host "Setting up default directories..." -ForegroundColor Yellow
try {
    $videosPath = Join-Path $env:USERPROFILE "Videos"
    $processedPath = Join-Path $videosPath "Processed"
    
    uv run content-cli config set-watch-dir $videosPath
    uv run content-cli config set-processed-dir $processedPath
    
    Write-Host "✓ Default directories configured" -ForegroundColor Green
} catch {
    Write-Host "⚠ WARNING: Could not set default directories" -ForegroundColor Yellow
    Write-Host "You can set them manually later with:" -ForegroundColor Cyan
    Write-Host "uv run content-cli config set-watch-dir <path>" -ForegroundColor Cyan
    Write-Host "uv run content-cli config set-processed-dir <path>" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API credentials" -ForegroundColor Cyan
Write-Host "2. Run: uv run content-cli auth all" -ForegroundColor Cyan
Write-Host "3. Run: uv run python main.py" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
