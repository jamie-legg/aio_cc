# Start the scheduler daemon
# This monitors scheduled posts and uploads them at their scheduled time

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "SCHEDULER DAEMON - AUTOMATED VIDEO POSTING" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""
Write-Host "This service will:" -ForegroundColor White
Write-Host "  ✓ Monitor scheduled posts every 60 seconds" -ForegroundColor Green
Write-Host "  ✓ Upload videos at their scheduled time" -ForegroundColor Green
Write-Host "  ✓ Handle retries for failed uploads" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Red
Write-Host "  • Videos will be posted automatically when their time arrives" -ForegroundColor Yellow
Write-Host "  • Check the dashboard first to review scheduled posts" -ForegroundColor Yellow
Write-Host "  • Press Ctrl+C to stop the scheduler at any time" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to start the scheduler, or Ctrl+C to cancel..." -ForegroundColor Cyan
Read-Host

# Start the scheduler daemon
python -m src.scheduling.scheduler_daemon


