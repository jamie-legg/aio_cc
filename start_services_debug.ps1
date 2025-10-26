# Start services with better error visibility
# This version will show you exactly what's failing

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "STARTING SERVICES WITH DEBUG OUTPUT" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if port 8000 is already in use
Write-Host "[TEST] Checking if port 8000 is available..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "  WARNING: Port 8000 is already in use!" -ForegroundColor Yellow
    Write-Host "  Process: $($port8000.OwningProcess)" -ForegroundColor Yellow
    Write-Host "  Killing the process..." -ForegroundColor Yellow
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Test 2: Check if port 5173 is already in use
Write-Host "[TEST] Checking if port 5173 is available..." -ForegroundColor Cyan
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    Write-Host "  WARNING: Port 5173 is already in use!" -ForegroundColor Yellow
    Write-Host "  Process: $($port5173.OwningProcess)" -ForegroundColor Yellow
    Write-Host "  Killing the process..." -ForegroundColor Yellow
    Stop-Process -Id $port5173.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Start the main script
uv run python scripts/start_all.py





