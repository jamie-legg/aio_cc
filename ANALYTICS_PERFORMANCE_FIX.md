# Analytics Dashboard Performance Fix

## Problem
The analytics dashboard was making **50+ individual API requests** to fetch metrics for each video when loading the top videos list. This caused:
- Excessive network traffic
- Slow page load times
- Poor user experience
- Server overload with many concurrent requests

## Root Cause
In `analytics-dashboard/src/components/AnalyticsDashboard.tsx`, the `fetchTopVideos` function was:
1. Fetching 50 videos from `/videos`
2. Making a separate request to `/metrics/{video_id}/latest?platform=...` for **each video**
3. This resulted in 51 total requests (1 for videos + 50 for metrics)

## Solution
Created an optimized endpoint that fetches videos with their metrics in a single database query:

### Backend Changes

1. **New Database Method** (`src/analytics/database.py`)
   - Added `get_top_videos_with_metrics()` method
   - Uses SQL JOIN to combine videos and their latest metrics
   - Single efficient query instead of N+1 queries

2. **New API Endpoint** (`src/analytics/api_server.py`)
   - Added `GET /videos/top-with-metrics`
   - Parameters: `limit` (default 10), `platform` (optional)
   - Returns videos with metrics pre-joined
   - **Important**: Placed before `/videos/{video_id}` route to prevent FastAPI path parameter matching

### Frontend Changes

1. **Updated Dashboard Component** (`analytics-dashboard/src/components/AnalyticsDashboard.tsx`)
   - Changed `fetchTopVideos()` to use new endpoint
   - Reduced from 51 requests to **1 single request**

2. **Updated API Service** (`analytics-dashboard/src/services/analyticsApi.ts`)
   - Added `getTopVideosWithMetrics()` method for consistency

## Performance Improvement

- **Before**: 51 HTTP requests (1 + 50)
- **After**: 1 HTTP request
- **Reduction**: ~98% fewer requests

## Benefits
- ✅ Faster page load times
- ✅ Reduced server load
- ✅ Better user experience
- ✅ More efficient database queries
- ✅ Scalable architecture

## Testing
After restarting the analytics API server, the dashboard should now make only 1 request to `/videos/top-with-metrics` instead of 50+ requests to `/latest`.

