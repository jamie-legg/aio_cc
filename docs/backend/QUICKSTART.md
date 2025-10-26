# Backend Quick Start Guide

## Prerequisites

- Docker & Docker Compose installed
- OpenAI API key (for AI features)
- Python 3.11+ (optional, for running without Docker)

## Setup

### Option 1: Automated Setup (Recommended)

```bash
cd backend
./setup_env.sh
```

This will:
- Generate secure JWT secret and encryption key
- Create `.env` file with sensible defaults
- Use Docker service names for database/Redis

### Option 2: Manual Setup

```bash
cd backend
cp .env.example .env
# Edit .env and fill in your values
```

**Required environment variables:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional environment variables:**
- `NGROK_AUTH_TOKEN` - For OAuth development
- `INSTAGRAM_CLIENT_ID/SECRET` - For Instagram integration
- `TIKTOK_CLIENT_KEY/SECRET` - For TikTok integration
- `STRIPE_SECRET_KEY` - For billing

## Start Backend

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)

### Check Status

```bash
docker-compose ps
docker-compose logs -f api
```

### Access API

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

## Create First User

### Using API Docs

1. Go to http://localhost:8000/docs
2. Open `POST /api/v1/auth/register`
3. Click "Try it out"
4. Enter your email and password
5. Click "Execute"

Example:
```json
{
  "email": "you@example.com",
  "password": "your-secure-password"
}
```

### Using curl

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"your-password"}'
```

Response will include your API key:
```json
{
  "id": 1,
  "email": "you@example.com",
  "api_key": "cc_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscription_tier": "free"
}
```

### Login to Get JWT Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"your-password"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "api_key": "cc_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## Configure Desktop Client

Use the API key from registration:

```bash
cd ..
uv run content-cli config set-backend \
  --api-key "cc_your_key_here" \
  --api-url "http://localhost:8000" \
  --use-backend true
```

## Test AI Enrichment

```bash
curl -X POST http://localhost:8000/api/v1/enrichment/generate \
  -H "X-API-Key: cc_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test_video.mp4","game_context":"gaming"}'
```

## Check Quota

```bash
curl http://localhost:8000/api/v1/enrichment/quota \
  -H "X-API-Key: cc_your_key_here"
```

## Stop Backend

```bash
docker-compose down
```

To also remove volumes (database data):
```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If port 8000 is in use:
```bash
# Find process
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Database Connection Error

```bash
# Check if postgres is running
docker-compose ps

# View postgres logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### API Not Responding

```bash
# View API logs
docker-compose logs -f api

# Check if services are healthy
docker-compose ps
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove .env (optional)
rm .env

# Start fresh
./setup_env.sh
docker-compose up -d
```

## Development Mode

To run the API with auto-reload:

```bash
# Edit docker-compose.yml and uncomment the volumes mount
# Then restart
docker-compose up -d api

# Logs will show file changes
docker-compose logs -f api
```

## Next Steps

1. **Configure Desktop Client** - See main README
2. **Set Up OAuth** - Add Instagram/YouTube/TikTok credentials
3. **Test Upload Flow** - Try uploading a video
4. **View Analytics** - Check dashboard at http://localhost:5173/dashboard
5. **Configure Stripe** - For subscription billing (production)

## API Endpoints Reference

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get tokens
- `GET /api/v1/auth/me` - Get user info

### AI Enrichment
- `POST /api/v1/enrichment/generate` - Generate metadata
- `GET /api/v1/enrichment/quota` - Check quota

### OAuth
- `POST /api/v1/oauth/{platform}/initiate` - Start OAuth
- `POST /api/v1/oauth/{platform}/callback` - Handle callback
- `GET /api/v1/oauth/{platform}/credentials` - Get credentials

### Analytics
- `POST /api/v1/analytics/track` - Track upload
- `GET /api/v1/analytics/overview` - Dashboard data
- `GET /api/v1/analytics/videos` - List videos
- `GET /api/v1/analytics/platforms` - Platform stats

Full API documentation: http://localhost:8000/docs



