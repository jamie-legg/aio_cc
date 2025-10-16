"""Configuration settings for the backend API."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str
    
    # OAuth Credentials
    instagram_client_id: str = ""
    instagram_client_secret: str = ""
    youtube_client_secrets_file: str = ""
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # ngrok
    ngrok_auth_token: str = ""
    ngrok_domain: str = ""
    
    # Subscription tiers
    free_tier_quota: int = 10
    pro_tier_quota: int = 100
    enterprise_tier_quota: int = -1  # Unlimited
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_allowed_origins(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()

