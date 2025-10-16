# SaaS Architecture Documentation

This document describes the transformation of the Content Creation tool into a SaaS platform.

## Architecture Overview

### Components

1. **Open Source Desktop Client** (Python)
   - File watcher for video files
   - Local video processing (FFmpeg)
   - Upload orchestration
   - Python GUI (tkinter)
   - CLI interface

2. **Proprietary Backend API** (FastAPI)
   - User authentication & API keys
   - AI enrichment proxy (OpenAI)
   - OAuth credential storage
   - Analytics collection
   - Quota management
   - Subscription billing (Stripe)

3. **Analytics Dashboard** (React)
   - Web-based dashboard
   - Real-time metrics
   - Platform performance
   - JWT authentication

4. **Marketing Website** (Static HTML/CSS/JS)
   - Landing page
   - Pricing tiers
   - Client downloads
   - Documentation

## Data Flow

```
[Desktop Client] 
    ↓ (watches directory)
    ↓ (detects video file)
    ↓ (processes locally with FFmpeg)
    ↓
[Backend API] ← (requests AI metadata)
    ↓ (returns title, caption, hashtags)
    ↓ (checks quota)
[Desktop Client]
    ↓ (gets OAuth credentials from backend)
    ↓ (uploads to platforms)
    ↓ (tracks analytics)
[Backend API]
    ↓ (stores metrics)
[Analytics Dashboard] ← (displays data)
```

## Subscription Tiers

### Free Tier
- 10 uploads/month
- 1 platform (Instagram OR YouTube OR TikTok)
- Community support
- Basic analytics

### Pro Tier ($29/month)
- 100 uploads/month
- All 3 platforms
- Priority support
- Advanced analytics
- Custom AI prompts

### Enterprise ($99/month)
- Unlimited uploads
- All platforms
- Dedicated support
- API access
- White-label options

## Security

### Desktop Client
- API key stored locally (encrypted)
- No OAuth tokens stored locally
- HTTPS-only communication
- Certificate pinning

### Backend API
- JWT for web authentication
- API keys for desktop clients
- OAuth tokens encrypted (Fernet)
- Rate limiting (Redis)
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration

### Data Storage
- Passwords: bcrypt hashing
- OAuth tokens: Fernet encryption
- API keys: Secure random generation
- Database: SSL/TLS connections
- Backups: Encrypted at rest

## Deployment

### Development
```bash
# Backend
cd backend
docker-compose up -d

# Desktop Client
cd ..
uv run content-gui
```

### Production (Kubernetes)
```bash
# Create secrets
kubectl create secret generic content-creation-secrets \
  --from-literal=database-url="..." \
  --from-literal=secret-key="..." \
  --from-literal=openai-api-key="..."

# Deploy services
kubectl apply -f backend/k8s/postgres.yaml
kubectl apply -f backend/k8s/redis.yaml
kubectl apply -f backend/k8s/deployment.yaml
kubectl apply -f backend/k8s/service.yaml
kubectl apply -f backend/k8s/ingress.yaml
```

### Docker (Single Server)
```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (returns JWT + API key)
- `GET /api/v1/auth/me` - Get user info
- `POST /api/v1/auth/refresh-api-key` - Regenerate API key

### AI Enrichment
- `POST /api/v1/enrichment/generate` - Generate metadata
- `GET /api/v1/enrichment/quota` - Check quota status

### OAuth Proxy
- `POST /api/v1/oauth/{platform}/initiate` - Start OAuth
- `POST /api/v1/oauth/{platform}/callback` - OAuth callback
- `GET /api/v1/oauth/{platform}/credentials` - Get credentials
- `DELETE /api/v1/oauth/{platform}/credentials` - Revoke

### Analytics
- `POST /api/v1/analytics/track` - Track upload
- `GET /api/v1/analytics/overview` - Dashboard overview
- `GET /api/v1/analytics/videos` - Video list
- `GET /api/v1/analytics/platforms` - Platform stats

## Client Configuration

### Environment Variables
```bash
# Backend API
BACKEND_API_URL=https://api.contentcreation.app
CONTENT_CREATION_API_KEY=cc_your_api_key_here
USE_BACKEND_API=true

# Fallback to local mode
USE_BACKEND_API=false  # Uses local OpenAI directly
```

### Config File
Location: `~/.content_creation/config.json`

```json
{
  "watch_dir": "/Users/jamie/Videos",
  "processed_dir": "/Users/jamie/Videos/Processed",
  "video_extensions": [".mov", ".mp4", ".avi"],
  "backend_api_url": "https://api.contentcreation.app",
  "api_key": "cc_...",
  "use_backend_api": true,
  "upload_to_instagram": true,
  "upload_to_youtube": true,
  "upload_to_tiktok": true
}
```

## Monetization Strategy

### Revenue Streams
1. **Subscriptions** (Primary)
   - Free → Pro conversion
   - Pro → Enterprise upsell
   - Annual discount (2 months free)

2. **Add-ons** (Future)
   - Additional platforms
   - Extra quota packs
   - Custom AI models
   - Priority processing

3. **Enterprise** (High-value)
   - Custom integrations
   - On-premise deployment
   - White-label licensing
   - Professional services

### Key Metrics
- Monthly Active Users (MAU)
- Free → Pro conversion rate
- Churn rate
- Customer Lifetime Value (LTV)
- Customer Acquisition Cost (CAC)
- LTV:CAC ratio target: 3:1

## Marketing Funnel

1. **Awareness**
   - Social media (show tool in action)
   - YouTube tutorials
   - Reddit/Discord communities
   - SEO (content creation tools)

2. **Interest**
   - Landing page with demo video
   - Feature comparison
   - Pricing transparency
   - Social proof (testimonials)

3. **Trial**
   - Free tier (no credit card)
   - Quick onboarding
   - First video in 5 minutes
   - In-app tips

4. **Conversion**
   - Quota notifications at 80%
   - "Upgrade for more" prompts
   - Feature unlocks (all platforms)
   - Annual discount offer

5. **Retention**
   - Regular feature updates
   - Email engagement
   - Success metrics
   - Community building

## Technical Roadmap

### Phase 1: MVP (Current)
- ✅ Backend API foundation
- ✅ Desktop client refactor
- ✅ Basic Python GUI
- ⏳ Analytics dashboard integration
- ⏳ Billing integration

### Phase 2: Beta
- ⏳ User onboarding flow
- ⏳ Payment processing (Stripe)
- ⏳ Email notifications
- ⏳ Usage analytics
- ⏳ Marketing website

### Phase 3: Launch
- ⏳ Production deployment
- ⏳ Monitoring & alerting
- ⏳ Customer support system
- ⏳ Documentation
- ⏳ Public launch

### Phase 4: Growth
- ⏳ Mobile app (iOS/Android)
- ⏳ Browser extension
- ⏳ Additional platforms (LinkedIn, Twitter)
- ⏳ Team accounts
- ⏳ API for developers

## Support & Documentation

### User Documentation
- Getting started guide
- Platform setup tutorials
- Troubleshooting FAQ
- Video tutorials
- API documentation

### Developer Documentation
- Backend API reference
- Desktop client architecture
- Deployment guides
- Contributing guidelines (open source client)

### Support Channels
- Free: Community Discord
- Pro: Email support (48h response)
- Enterprise: Dedicated Slack channel + phone

## Compliance

### Data Protection
- GDPR compliance
- Privacy policy
- Terms of service
- Data retention policy
- Right to deletion

### Platform Compliance
- Instagram API terms
- YouTube API terms
- TikTok API terms
- Stripe PCI compliance

## Monitoring & Observability

### Metrics
- API response times
- Error rates
- Quota usage
- Upload success rates
- User activity

### Tools
- Prometheus + Grafana (metrics)
- Sentry (error tracking)
- PostHog (product analytics)
- Stripe Dashboard (billing)

### Alerts
- API downtime
- High error rates
- Database issues
- Quota exceeded
- Payment failures

## Backup & Recovery

### Database Backups
- Automated daily backups
- Point-in-time recovery
- Encrypted storage
- 30-day retention
- Disaster recovery plan

### Application Backups
- Docker images tagged
- Configuration in Git
- Secrets in vault
- Documented restore procedure

## Cost Structure

### Infrastructure (est. per month)
- Kubernetes cluster: $100-300
- PostgreSQL (managed): $50-100
- Redis (managed): $30-50
- Object storage: $10-20
- CDN: $20-50
- **Total: ~$210-520/month**

### Services
- OpenAI API: Pay-per-use (~$0.002 per request)
- Stripe: 2.9% + $0.30 per transaction
- ngrok (optional): $8-20/month
- Domain & SSL: $20/year

### Profitability
- Break-even: ~20 Pro subscribers
- Target: 100+ Pro subscribers in first 6 months
- MRR goal: $2,900+ (100 × $29)
- Profit margin: 60-70% after costs

