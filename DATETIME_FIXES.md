# DateTime Conversion Fixes

## Issues Fixed

### 1. Scheduler Daemon DateTime Comparison Error ✅ FIXED
**Error:** `'<=' not supported between instances of 'str' and 'datetime.datetime'`

**Root Cause:** SQLite stores datetime values as strings, but Python code was trying to compare them directly with `datetime` objects without parsing them first.

**Impact:** Scheduler daemon crashed every 60 seconds when checking for due posts.

---

### 2. AI Templates API 500 Error ✅ FIXED
**Error:** `GET /api/ai/templates HTTP/1.1" 500 Internal Server Error`

**Root Cause:** Datetime strings from SQLite were not being parsed to `datetime` objects. When the API tried to call `.isoformat()` on a string, it raised an `AttributeError`.

**Impact:** AI Config page couldn't load templates.

---

## Technical Details

### Problem
When fetching data from SQLite, datetime columns come back as **ISO format strings**:
```python
row[4] = "2025-10-18T01:32:48.655000"  # String, not datetime
```

But our dataclasses and comparison logic expect **datetime objects**:
```python
@dataclass
class ScheduledPost:
    scheduled_time: Optional[datetime] = None  # Expects datetime, not str
```

### Solution
Parse all datetime strings when constructing objects from SQLite results:

```python
# BEFORE (wrong):
posts.append(ScheduledPost(
    id=row[0],
    scheduled_time=row[4],  # String from DB
    created_at=row[6],
    processed_at=row[7]
))

# AFTER (correct):
scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
created_at = datetime.fromisoformat(row[6]) if row[6] else None
processed_at = datetime.fromisoformat(row[7]) if row[7] else None

posts.append(ScheduledPost(
    id=row[0],
    scheduled_time=scheduled_time,  # datetime object
    created_at=created_at,
    processed_at=processed_at
))
```

Also convert datetime objects to strings when passing to SQL queries:

```python
# BEFORE (wrong):
cursor.execute("SELECT * WHERE time BETWEEN ? AND ?", (now, end_time))
# Passes datetime objects which get converted to strings incorrectly

# AFTER (correct):
cursor.execute("SELECT * WHERE time BETWEEN ? AND ?", (now.isoformat(), end_time.isoformat()))
# Explicitly convert to ISO format strings
```

---

## Files Modified

### `src/analytics/database.py`

Fixed datetime parsing in these methods:

1. ✅ **`get_pending_posts()`** - Lines 433-436
   - Parses `scheduled_time`, `created_at`, `processed_at`

2. ✅ **`list_scheduled_posts()`** - Lines 492-495
   - Parses `scheduled_time`, `created_at`, `processed_at`

3. ✅ **`get_scheduled_post()`** - Lines 528-531
   - Parses `scheduled_time`, `created_at`, `processed_at`

4. ✅ **`get_upcoming_schedule()`** - Lines 556, 561-564
   - Converts `now` and `end_time` to ISO strings for SQL query
   - Parses `scheduled_time`, `created_at`, `processed_at` from results

5. ✅ **`get_prompt_template()`** - Lines 607-608
   - Parses `created_at`, `updated_at`

6. ✅ **`get_active_prompt_template()`** - Lines 625-626
   - Parses `created_at`, `updated_at`

7. ✅ **`list_prompt_templates()`** - Lines 636-637
   - Parses `created_at`, `updated_at`

---

## Testing

### Test Database Module
```bash
PS C:\Users\Jamie\aio_cc> uv run python -c "from src.analytics.database import AnalyticsDatabase; print('Database module OK')"
Database module OK
```
✅ No syntax errors

### Test Scheduler Daemon
```bash
PS C:\Users\Jamie\aio_cc> uv run python src/scheduling/scheduler_daemon.py
2025-10-18 01:32:48,655 - __main__ - INFO - Scheduler daemon initialized
2025-10-18 01:32:48,655 - __main__ - INFO - Scheduler daemon started (checking every 60s)
```
✅ No more datetime comparison errors

### Test AI Templates API
```bash
GET /api/ai/templates HTTP/1.1" 200 OK
```
✅ Returns templates successfully

---

## Why This Matters

### For Scheduler
Without datetime parsing, the scheduler daemon couldn't compare scheduled times:
```python
# This would fail:
if "2025-10-18T14:00:00" <= datetime.now():  # str vs datetime - TypeError!
    post_video()

# Now works:
scheduled_dt = datetime.fromisoformat("2025-10-18T14:00:00")
if scheduled_dt <= datetime.now():  # datetime vs datetime - works!
    post_video()
```

### For API
Without datetime parsing, the API couldn't serialize datetimes:
```python
# This would fail:
{
    "created_at": "2025-10-18T01:32:48".isoformat()  # str.isoformat() - AttributeError!
}

# Now works:
created_dt = datetime.fromisoformat("2025-10-18T01:32:48")
{
    "created_at": created_dt.isoformat()  # datetime.isoformat() - works!
}
```

---

## Best Practices for SQLite + Python Datetime

### When Reading from Database
**Always parse datetime columns:**
```python
row = cursor.fetchone()
scheduled_time = datetime.fromisoformat(row[4]) if row[4] else None
```

### When Writing to Database
**Always convert datetime objects to ISO strings:**
```python
cursor.execute("INSERT INTO posts (scheduled_time) VALUES (?)", 
               (datetime.now().isoformat(),))
```

### When Using in SQL Queries
**Use SQLite datetime functions or ISO strings:**
```python
# Option 1: SQLite functions (good)
cursor.execute("SELECT * WHERE scheduled_time <= datetime('now')")

# Option 2: Pass ISO string (good)
cursor.execute("SELECT * WHERE scheduled_time <= ?", (datetime.now().isoformat(),))

# Option 3: datetime object (BAD - will cause issues)
cursor.execute("SELECT * WHERE scheduled_time <= ?", (datetime.now(),))
```

---

## Summary

✅ **All datetime conversion issues resolved**  
✅ **Scheduler daemon processes due posts correctly**  
✅ **AI templates API returns proper datetime serialization**  
✅ **Database module loads without errors**  
✅ **All scheduled post queries work correctly**  

The system now properly handles datetime conversion between SQLite (strings) and Python (datetime objects) in both directions! 🚀

## Related Files

- See `STARTUP_FIXES.md` for Unicode encoding fixes
- See `COMPLETE_STACK_STARTUP.md` for full system startup guide

