# Content Creation Pipeline - Makefile
# Common commands and aliases for development and operations

.PHONY: help install dev test clean lint format sync-analytics start-analytics collect-metrics sync-channels generate-transition reset-youtube reset-instagram reset-tiktok

# Default target
help:
	@echo "Content Creation Pipeline - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install          Install dependencies"
	@echo "  dev              Install in development mode"
	@echo ""
	@echo "🎬 Content Creation:"
	@echo "  generate-transition  Generate Tron lightbike transition (interactive)"
	@echo "  test-sora           Test Sora 2 generation with custom prompt"
	@echo "  list-transitions     List generated transitions"
	@echo "  check-status         Check transition generation status"
	@echo "  add-outro           Add outro image to video(s)"
	@echo "  create-test-videos  Create test videos for testing"
	@echo "  test-outro          Test outro on a sample video"
	@echo ""
	@echo "📊 Analytics & Monitoring:"
	@echo "  start-analytics   Start the analytics API server"
	@echo "  start-dashboard   Start the analytics dashboard UI"
	@echo "  sync-channels     Sync videos from all authenticated channels"
	@echo "  collect-metrics   Collect metrics from all platforms"
	@echo "  total-views       Show total views across all platforms"
	@echo ""
	@echo "🔐 Authentication:"
	@echo "  auth-youtube      Authenticate with YouTube"
	@echo "  auth-instagram    Authenticate with Instagram"
	@echo "  auth-tiktok       Authenticate with TikTok"
	@echo "  auth-all          Authenticate with all platforms"
	@echo ""
	@echo "🔄 Reset Authentication:"
	@echo "  reset-youtube     Reset YouTube authentication and data"
	@echo "  reset-instagram   Reset Instagram authentication and data"
	@echo "  reset-tiktok      Reset TikTok authentication and data"
	@echo ""
	@echo "⏰ Scheduling:"
	@echo "  schedule-add      Schedule a video for posting (VIDEO=path TIME=\"YYYY-MM-DD HH:MM\" PLATFORMS=youtube,instagram,tiktok)"
	@echo "  schedule-list     List scheduled posts (optional: STATUS=pending PLATFORM=youtube)"
	@echo "  schedule-remove   Cancel a scheduled post (ID=1)"
	@echo "  schedule-status   Show scheduler status and upcoming posts"
	@echo "  scheduler-run     Run scheduler daemon (optional: INTERVAL=60)"
	@echo "  scheduler-once    Run scheduler once and exit (for cron)"
	@echo ""
	@echo "🛠️  Development:"
	@echo "  test              Run tests"
	@echo "  lint              Run linting"
	@echo "  format            Format code"
	@echo "  clean             Clean temporary files and caches"
	@echo ""
	@echo "📋 Utilities:"
	@echo "  status            Show system status"
	@echo "  logs              Show recent logs"
	@echo "  db-reset          Reset analytics database"

# Setup & Installation
install:
	@echo "📦 Installing dependencies..."
	uv pip install -e .

dev:
	@echo "🔧 Installing in development mode..."
	uv pip install -e .[dev]

# Content Creation
generate-transition:
	@echo "🎬 Generating Tron lightbike transition..."
	@read -p "Enter your transition prompt: " prompt; \
	uv run content-cli transitions generate --prompt "$$prompt"

test-sora:
	@echo "🧪 Testing Sora 2 generation..."
	@read -p "Enter your test prompt: " prompt; \
	uv run scripts/content/gen.py -p "$$prompt"

list-transitions:
	@echo "📋 Listing generated transitions..."
	uv run content-cli transitions list

check-status:
	@echo "🔍 Checking transition status..."
	uv run content-cli transitions status

add-outro:
	@echo "🎬 Adding outro image to video(s)..."
	@read -p "Enter video file or directory path: " path; \
	python add_outro_batch.py "$$path"

create-test-videos:
	@echo "🎥 Creating test videos..."
	python scripts/content/create_test_videos.py

test-outro:
	@echo "🧪 Testing outro functionality..."
	python test_outro.py

# Analytics & Monitoring
start-analytics:
	@echo "🚀 Starting analytics API server..."
	uv run scripts/analytics/start_analytics.py

start-dashboard:
	@echo "🎨 Starting analytics dashboard..."
	cd analytics-dashboard && npm run dev

sync-channels:
	@echo "📥 Syncing videos from all channels..."
	uv run scripts/analytics/sync_channels.py

collect-metrics:
	@echo "📊 Collecting metrics from all platforms..."
	uv run scripts/analytics/collect_metrics.py

total-views:
	@echo "🎯 Getting total views across all platforms..."
	uv run scripts/analytics/sync_channels.py --total-views-only

# Authentication
auth-youtube:
	@echo "🔐 Authenticating with YouTube..."
	uv run content-cli auth youtube

auth-instagram:
	@echo "🔐 Authenticating with Instagram..."
	uv run content-cli auth instagram

auth-tiktok:
	@echo "🔐 Authenticating with TikTok..."
	uv run content-cli auth tiktok

auth-all:
	@echo "🔐 Authenticating with all platforms..."
	uv run content-cli auth youtube
	uv run content-cli auth instagram
	uv run content-cli auth tiktok

auth-check:
	@echo "🔍 Checking authentication status..."
	uv run content-cli check all

# Reset Authentication
reset-youtube:
	@echo "🔄 Resetting YouTube authentication and data..."
	uv run content-cli reset youtube

reset-instagram:
	@echo "🔄 Resetting Instagram authentication and data..."
	uv run content-cli reset instagram

reset-tiktok:
	@echo "🔄 Resetting TikTok authentication and data..."
	uv run content-cli reset tiktok

# Development
test:
	@echo "🧪 Running tests..."
	uv run python -m pytest tests/ -v

lint:
	@echo "🔍 Running linting..."
	uv run ruff check src/ --fix

format:
	@echo "✨ Formatting code..."
	uv run ruff format src/

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/

# Utilities
status:
	@echo "📊 System Status:"
	@echo "=================="
	@echo "🔐 Authentication Status:"
	@uv run python -c "from src.managers.oauth_manager import OAuthManager; om = OAuthManager(); platforms = ['youtube', 'instagram', 'tiktok']; [print(f'  {p.upper()}: {\"✅\" if om.is_authenticated(p) else \"❌\"}') for p in platforms]"
	@echo ""
	@echo "📊 Analytics Database:"
	@if [ -f analytics.db ]; then echo "  Database: ✅ Exists"; else echo "  Database: ❌ Missing"; fi
	@echo ""
	@echo "🎬 Generated Content:"
	@if [ -d generated_transitions ]; then echo "  Transitions: ✅ $(ls generated_transitions/*/ 2>/dev/null | wc -l) categories"; else echo "  Transitions: ❌ None"; fi

logs:
	@echo "📋 Recent logs (last 20 lines):"
	@tail -n 20 *.log 2>/dev/null || echo "No log files found"

db-reset:
	@echo "🗑️  Resetting analytics database..."
	@read -p "Are you sure? This will delete all analytics data (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -f analytics.db; \
		echo "✅ Database reset complete"; \
	else \
		echo "❌ Database reset cancelled"; \
	fi

## Scheduling
# Schedule a video for posting
# Usage: make schedule-add VIDEO=path/to/video.mp4 TIME="2025-10-15 10:00" PLATFORMS=youtube,instagram,tiktok
schedule-add:
	@if [ -z "$(VIDEO)" ]; then \
		echo "❌ Error: VIDEO parameter required"; \
		echo "Usage: make schedule-add VIDEO=path/to/video.mp4 TIME=\"2025-10-15 10:00\" PLATFORMS=youtube,instagram,tiktok"; \
		exit 1; \
	fi
	@if [ -z "$(TIME)" ]; then \
		echo "❌ Error: TIME parameter required"; \
		echo "Usage: make schedule-add VIDEO=path/to/video.mp4 TIME=\"2025-10-15 10:00\" PLATFORMS=youtube,instagram,tiktok"; \
		exit 1; \
	fi
	@if [ -z "$(PLATFORMS)" ]; then \
		echo "❌ Error: PLATFORMS parameter required"; \
		echo "Usage: make schedule-add VIDEO=path/to/video.mp4 TIME=\"2025-10-15 10:00\" PLATFORMS=youtube,instagram,tiktok"; \
		exit 1; \
	fi
	uv run content-cli schedule add "$(VIDEO)" --time "$(TIME)" --platforms "$(PLATFORMS)" \
		$(if $(TITLE),--title "$(TITLE)") \
		$(if $(CAPTION),--caption "$(CAPTION)") \
		$(if $(HASHTAGS),--hashtags "$(HASHTAGS)")

# List scheduled posts
# Usage: make schedule-list [STATUS=pending] [PLATFORM=youtube]
schedule-list:
	uv run content-cli schedule list \
		$(if $(STATUS),--status $(STATUS)) \
		$(if $(PLATFORM),--platform $(PLATFORM))

# Cancel a scheduled post
# Usage: make schedule-remove ID=1
schedule-remove:
	@if [ -z "$(ID)" ]; then \
		echo "❌ Error: ID parameter required"; \
		echo "Usage: make schedule-remove ID=1"; \
		exit 1; \
	fi
	uv run content-cli schedule remove $(ID)

# Show scheduler status
schedule-status:
	uv run content-cli schedule status

# Run scheduler daemon
# Usage: make scheduler-run [INTERVAL=60]
scheduler-run:
	uv run content-cli schedule run $(if $(INTERVAL),--interval $(INTERVAL))

# Run scheduler once (for cron jobs)
scheduler-once:
	uv run content-cli schedule run --once

# Quick aliases
sync: sync-channels
metrics: collect-metrics
views: total-views
start: start-analytics
test: test-sora
