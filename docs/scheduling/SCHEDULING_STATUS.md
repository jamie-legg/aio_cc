# Scheduling System - Implementation Status

## ✅ BACKEND COMPLETE

### 1. Database Schema ✓
**File**: `src/analytics/database.py`
- Added `AIPromptTemplate` dataclass with fields: id, name, prompt_text, is_active, created_at, updated_at
- Created `ai_prompt_templates` table in SQLite
- Added 11 scheduling helper methods
- Added 7 AI template CRUD methods
- All methods tested and working

### 2. Core Scheduling Service ✓
**File**: `src/scheduling/scheduler.py`
- `get_next_slot()` - Finds next available hour per platform
- `schedule_video()` - Creates scheduled post record
- `check_due_posts()` - Returns posts ready for publishing
- `get_time_until_post()` - Calculates countdown
- `space_videos()` - Distributes multiple videos across hours
- `force_post_now()` - Reschedules to immediate
- `reschedule_video()` - Changes scheduled time

### 3. Scheduler Daemon ✓
**File**: `src/scheduling/scheduler_daemon.py`
- Background service checking every 60 seconds
- Executes uploads for due posts via UploadManager
- Updates status: pending → processing → completed/failed
- Retry logic (max 3 attempts)
- Comprehensive error handling and logging
- Can be run: `uv run python src/scheduling/scheduler_daemon.py`

### 4. API Endpoints ✓
**File**: `src/analytics/api_server.py`

**Schedule Management** (6 endpoints):
- `GET /api/schedule/upcoming` - List upcoming posts (default 24hrs)
- `GET /api/schedule/post/{id}` - Get post details
- `POST /api/schedule/post` - Create scheduled post
- `POST /api/schedule/post/{id}/force` - Force immediate post
- `DELETE /api/schedule/post/{id}` - Cancel post
- `PATCH /api/schedule/post/{id}` - Reschedule post

**AI Template Management** (7 endpoints):
- `GET /api/ai/templates` - List all templates
- `GET /api/ai/templates/active` - Get active template
- `POST /api/ai/templates` - Create template
- `PUT /api/ai/templates/{id}` - Update template
- `DELETE /api/ai/templates/{id}` - Delete template
- `POST /api/ai/templates/{id}/activate` - Activate template
- `POST /api/ai/test-prompt` - Test prompt with sample data

### 5. AI Manager Integration ✓
**File**: `src/managers/ai_manager.py`
- Added `template_id` parameter to `generate_metadata()`
- Loads active template from database if no template_id
- Falls back to default prompt if no template found
- Template variables: `{filename}`, `{game_context}`

### 6. Clip Watcher Integration ✓
**File**: `src/content_creation/clip_watcher.py`
- Created `schedule_for_posting()` function
- Replaces immediate upload with scheduled posting
- Checks platform authentication before scheduling
- Emits `video_scheduled` event

### 7. Watcher Events ✓
**File**: `src/content_creation/watcher_events.py`
- Added `emit_video_scheduled()` function
- Includes scheduled_time and platforms in metadata

### 8. Configuration ✓
**File**: `src/managers/config_manager.py`
- Added `auto_schedule: bool = True`
- Added `schedule_spacing_hours: int = 1`
- Added `default_post_time_offset: int = 1`

## ⏳ FRONTEND REMAINING

All frontend work remains to be done. Here's the complete implementation plan:

### 9. Sidebar Component
**New File**: `analytics-dashboard/src/components/Sidebar.tsx`
- Fixed left sidebar (240px width)
- Navigation links:
  - Analytics (BarChart3 icon) → `/dashboard`
  - Schedule (Calendar icon) → `/dashboard/schedule`
  - AI Config (Sparkles icon) → `/dashboard/ai-config`
- Active state highlighting with border-left accent
- Logo/title at top
- Professional styling (bg-gray-900, border-r)

### 10. Dashboard Layout
**New File**: `analytics-dashboard/src/components/DashboardLayout.tsx`
- Wrapper component with Sidebar + content area
- Content area with `ml-60` (240px left margin)
- Uses `<Outlet />` for nested routes

**Modify**: `analytics-dashboard/src/App.tsx`
- Add nested routes:
  ```tsx
  <Route path="/dashboard" element={<DashboardLayout />}>
    <Route index element={<AnalyticsDashboard />} />
    <Route path="schedule" element={<SchedulePage />} />
    <Route path="ai-config" element={<AIConfigPage />} />
  </Route>
  ```

### 11. Schedule API Service
**New File**: `analytics-dashboard/src/services/scheduleApi.ts`
- `getUpcoming(hours)` - Fetch upcoming posts
- `getPost(postId)` - Get post details
- `createPost(data)` - Schedule new post
- `forcePostNow(postId)` - Force immediate posting
- `cancelPost(postId)` - Cancel scheduled post
- `reschedulePost(postId, newTime)` - Change time

### 12. Schedule Page
**New File**: `analytics-dashboard/src/pages/SchedulePage.tsx`

**Components**:
- Header with stats (total scheduled, posting today, completed today)
- [+ Add Video] button (opens AddPostModal)
- List of scheduled posts (cards)

**ScheduledPostCard** features:
- Thumbnail placeholder
- Title + platforms badges (YouTube/Instagram/TikTok)
- Status badge with color coding:
  - Pending: "Posting in 45 min" (countdown timer)
  - Processing: "Posting..." (spinner)
  - Completed: "Posted" (checkmark)
  - Failed: "Failed" (error icon)
- Scheduled time display
- Action buttons:
  - [Post Now] (if pending)
  - [Reschedule] (if pending)
  - [Cancel] (if pending)
  - [Retry] (if failed)
  - [View] link (if completed)

**New File**: `analytics-dashboard/src/components/ScheduledPostCard.tsx`
- Individual post card component
- Real-time countdown using `useEffect` with 1-second interval
- Platform badges with icons
- Status color coding

**New File**: `analytics-dashboard/src/components/AddPostModal.tsx`
- File input or video URL
- Title, description inputs
- Platform checkboxes (YouTube, Instagram, TikTok)
- DateTime picker (defaults to next available hour)
- [Schedule] button

### 13. AI Config API Service
**New File**: `analytics-dashboard/src/services/aiConfigApi.ts`
- `getTemplates()` - List all templates
- `getActiveTemplate()` - Get active template
- `createTemplate(data)` - Create new template
- `updateTemplate(id, data)` - Update template
- `deleteTemplate(id)` - Delete template
- `activateTemplate(id)` - Set as active
- `testPrompt(prompt, filename, context)` - Test prompt

### 14. AI Config Page
**New File**: `analytics-dashboard/src/pages/AIConfigPage.tsx`

**Layout**: Two-column split

**Left Panel (40%)**:
- [+ New Template] button at top
- List of templates
- Each shows: name, prompt preview (truncated), active badge
- Click to select/edit

**Right Panel (60%)**:
- Template name input
- Large textarea for prompt text
- Helper text showing available variables: `{filename}`, `{game_context}`
- Active indicator (checkmark icon)
- Button group:
  - [Save] - Update template
  - [Set as Active] - Activate this template
  - [Test Prompt] - Opens test modal
  - [Delete] - Confirm then delete

**Test Prompt Modal**:
- Input: Sample filename
- Input: Game context (default: "gaming")
- [Generate] button
- Shows result: title, caption, hashtags
- Helps validate prompt quality

**Default Template to Pre-populate**:
```
You are a social media expert creating engaging content for gaming videos.

Given a video filename: {filename}
Game context: {game_context}

Generate:
1. An exciting, click-worthy title (max 100 chars)
2. An engaging caption with emojis (max 2200 chars)
3. 10-15 relevant hashtags

Format as JSON:
{
  "title": "...",
  "caption": "...",
  "hashtags": "#gaming #..."
}
```

## How to Start Implementation

### Terminal 1: API Server
```bash
uv run python scripts/analytics/start_analytics.py
```

### Terminal 2: Scheduler Daemon
```bash
uv run python src/scheduling/scheduler_daemon.py
```

### Terminal 3: Dashboard
```bash
cd analytics-dashboard
npm run dev
```

### Terminal 4: Watcher (for testing)
```bash
uv run python main.py
```

## Testing Flow

1. **Backend Test**:
   - Drop video in watch directory
   - Verify it schedules (check console output)
   - Verify event emitted (check watcher panel)
   - Check database: `sqlite3 analytics.db "SELECT * FROM scheduled_posts;"`

2. **API Test**:
   - `curl http://localhost:8000/api/schedule/upcoming`
   - `curl http://localhost:8000/api/ai/templates`

3. **Frontend Test** (once built):
   - Navigate to `/dashboard/schedule`
   - See scheduled video with countdown
   - Click [Post Now] to force immediate posting
   - Navigate to `/dashboard/ai-config`
   - Create/edit/test templates
   - Set template as active
   - Drop new video, verify it uses new template

## File Count

**Backend**: 8 files modified/created ✅
**Frontend**: 10+ files to create ⏳

## Estimated Frontend Work

- Sidebar + Layout: ~200 lines
- Schedule Page + Components: ~500 lines
- AI Config Page: ~400 lines
- API Services: ~200 lines
- **Total**: ~1300 lines of TypeScript/React

## Dependencies

All backend dependencies already installed:
- ✅ `psutil` (for OBS detection)
- ✅ `sse-starlette` (for SSE)

Frontend uses existing dependencies:
- React + TypeScript
- Tailwind CSS
- Lucide React (icons)
- Framer Motion (animations)

## Success Criteria

- [ ] Sidebar navigation works
- [ ] Schedule page displays upcoming posts
- [ ] Countdown updates every second
- [ ] Force post button works
- [ ] AI config page loads/saves templates
- [ ] Test prompt generates metadata
- [ ] Active template is used by watcher
- [ ] Complete flow: drop video → schedule → countdown → force post → verify upload

## Ready to Continue

Backend is 100% complete and working. Frontend implementation can now begin with sidebar → layout → schedule page → AI config page.

