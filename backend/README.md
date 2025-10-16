# Content Creation Backend API

Backend API server for the Content Creation SaaS platform.

## Features

- **User Authentication**: JWT tokens and API keys
- **AI Enrichment**: Proxy OpenAI requests with quota tracking
- **OAuth Proxy**: Secure OAuth flow handling for social platforms
- **Analytics**: Track and analyze upload performance
- **Quota Management**: Tiered subscription quotas
- **Rate Limiting**: Redis-based rate limiting

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis locally
# (or use docker-compose for just databases)

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `OPENAI_API_KEY`: OpenAI API key
- `STRIPE_SECRET_KEY`: Stripe API key (for billing)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token + API key
- `GET /api/v1/auth/me` - Get current user info

### AI Enrichment
- `POST /api/v1/enrichment/generate` - Generate metadata (requires API key)
- `GET /api/v1/enrichment/quota` - Check quota status

### OAuth Proxy
- `POST /api/v1/oauth/{platform}/initiate` - Start OAuth flow
- `POST /api/v1/oauth/{platform}/callback` - Handle OAuth callback
- `GET /api/v1/oauth/{platform}/credentials` - Get stored credentials
- `DELETE /api/v1/oauth/{platform}/credentials` - Delete credentials

### Analytics
- `POST /api/v1/analytics/track` - Track upload event
- `GET /api/v1/analytics/overview` - Get dashboard overview
- `GET /api/v1/analytics/videos` - List uploaded videos
- `GET /api/v1/analytics/platforms` - Platform statistics

## Database Schema

- `users` - User accounts
- `subscriptions` - Subscription and quota tracking
- `uploads` - Upload history
- `oauth_credentials` - Encrypted OAuth tokens

## Security

- Passwords hashed with bcrypt
- OAuth tokens encrypted with Fernet
- JWT tokens for web dashboard
- API keys for desktop client
- Rate limiting on all endpoints
- CORS configuration

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

See `k8s/` directory for Kubernetes manifests for cloud deployment.

## License

Proprietary - All rights reserved

