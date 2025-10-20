# Start all services (watcher, API, dashboard) in parallel with unified output
# This script runs all three services and shows their output in one terminal

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Content Creation Platform - Starting" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to run a command and prefix its output
function Start-ServiceWithPrefix {
    param(
        [string]$ServiceName,
        [string]$Command,
        [string]$Color,
        [string]$WorkingDirectory = $PWD
    )
    
    $job = Start-Job -ScriptBlock {
        param($cmd, $name, $dir)
        Set-Location $dir
        Invoke-Expression $cmd 2>&1 | ForEach-Object {
            "[$name] $_"
        }
    } -ArgumentList $Command, $ServiceName, $WorkingDirectory
    
    return $job
}

# Start the three services
Write-Host "[INFO] Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start clip watcher
Write-Host "[WATCHER] Starting clip watcher..." -ForegroundColor Green
$watcherJob = Start-ServiceWithPrefix -ServiceName "WATCHER" -Command "uv run python main.py" -Color "Green"

# Start analytics API
Write-Host "[API] Starting analytics API server..." -ForegroundColor Blue
$apiJob = Start-ServiceWithPrefix -ServiceName "API" -Command "uv run python -m src.analytics.api_server" -Color "Blue"

# Wait a moment for API to start
Start-Sleep -Seconds 2

# Start dashboard
Write-Host "[DASHBOARD] Starting analytics dashboard..." -ForegroundColor Magenta
$dashboardJob = Start-ServiceWithPrefix -ServiceName "DASHBOARD" -Command "npm run dev" -Color "Magenta" -WorkingDirectory (Join-Path $PWD "analytics-dashboard")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All Services Started!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[WATCHER]   Monitoring videos folder" -ForegroundColor Green
Write-Host "[API]       http://localhost:8000" -ForegroundColor Blue
Write-Host "[DASHBOARD] http://localhost:5173/dashboard" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Monitor all jobs and display output
$jobs = @($watcherJob, $apiJob, $dashboardJob)
$colors = @{
    "WATCHER" = "Green"
    "API" = "Blue"
    "DASHBOARD" = "Magenta"
}

try {
    while ($true) {
        foreach ($job in $jobs) {
            $output = Receive-Job $job -ErrorAction SilentlyContinue
            if ($output) {
                foreach ($line in $output) {
                    # Extract service name from line
                    if ($line -match '^\[(\w+)\]') {
                        $serviceName = $Matches[1]
                        $color = $colors[$serviceName]
                        if ($color) {
                            Write-Host $line -ForegroundColor $color
                        } else {
                            Write-Host $line
                        }
                    } else {
                        Write-Host $line
                    }
                }
            }
            
            # Check if job failed
            if ($job.State -eq "Failed") {
                Write-Host "[ERROR] Service failed: $($job.Name)" -ForegroundColor Red
            }
        }
        Start-Sleep -Milliseconds 100
    }
} catch {
    Write-Host "`n[INFO] Stopping all services..." -ForegroundColor Yellow
} finally {
    # Clean up jobs
    $jobs | Stop-Job -ErrorAction SilentlyContinue
    $jobs | Remove-Job -ErrorAction SilentlyContinue
    Write-Host "[INFO] All services stopped" -ForegroundColor Yellow
}


