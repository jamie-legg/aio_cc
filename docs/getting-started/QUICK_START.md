# Quick Start Guide

## If Services Crash or Won't Start

### Problem: "API died" or ports already in use

**Solution: Clean up zombie processes**

```powershell
# Kill all Python and Node processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Now start fresh
make start
```

Or use the debug startup script:
```powershell
.\start_services_debug.ps1
```

## Normal Startup

### 1. Clear Old Data (First Time or After Issues)

```powershell
python clear_and_start_fresh.py
```

### 2. Start All Services

```powershell
make start
```

This starts:
- Clip Watcher (monitors video folder)
- Analytics API (backend on port 8000)
- Scheduler Daemon (auto-posts scheduled videos)
- Dashboard (web UI on port 5173)

### 3. Open Dashboard

The dashboard opens automatically, or visit:
```
http://localhost:5173/uploads
```

### 4. Schedule Videos

Go to **"Missed Replays"** section:
1. Check boxes next to videos you want to schedule
2. Click "Schedule Selected"
3. Confirm the dialog
4. Videos appear in "Scheduled Uploads" section above

## Common Issues

### Services crash immediately after starting

**Cause:** Dashboard dependency issues or port conflicts

**Fix:**
```powershell
# Clean up ports
.\start_services_debug.ps1

# Or manually:
Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force
cd analytics-dashboard
npm install
cd ..
make start
```

### "Port already in use" error

**Fix:**
```powershell
# Find and kill processes using ports 8000 and 5173
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Then restart
make start
```

### Dashboard shows errors or blank page

**Fix:**
```powershell
cd analytics-dashboard
npm install
cd ..
make start
```

### API not responding

**Fix:**
```powershell
# Check if running
Test-NetConnection localhost -Port 8000

# If not, restart services
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
make start
```

### Videos posting immediately instead of scheduling

**Fix:**
```powershell
# Stop services
# Press Ctrl+C in the terminal

# Clear old posts
python clear_and_start_fresh.py

# Restart
make start

# Use "Missed Replays" section to schedule properly
```

## Stopping Services

Press **Ctrl+C** in the terminal where you ran `make start`

All services will stop gracefully.

## File Reference

- **`clear_and_start_fresh.py`** - Clear scheduled posts and failed uploads
- **`start_services_debug.ps1`** - Start with automatic port cleanup
- **`SAFE_SCHEDULING_WORKFLOW.md`** - Complete scheduling guide
- **`SCHEDULING_SAFETY_GUIDE.md`** - Detailed safety documentation

## Quick Commands

| Task | Command |
|------|---------|
| Start everything | `make start` |
| Start with cleanup | `.\start_services_debug.ps1` |
| Clear old data | `python clear_and_start_fresh.py` |
| Kill all processes | `Get-Process python,node -EA SilentlyContinue \| Stop-Process -Force` |
| Open dashboard | `http://localhost:5173/uploads` |
| Check API | `Test-NetConnection localhost -Port 8000` |

## After Starting

1. Dashboard opens automatically at http://localhost:5173
2. Go to "Uploads" page
3. Use "Missed Replays" section to schedule videos
4. Check "Scheduled Uploads" to see your schedule
5. Videos post automatically at their scheduled times

## Safety Reminder

With `AUTO_SCHEDULE=true`:
- New videos from watch folder are **scheduled**, not posted immediately
- Use "Missed Replays" to control when videos post
- Confirmation dialogs prevent accidental bulk posting
- Cancel or adjust anytime before scheduled time




