#!/usr/bin/env python3
"""Initialize the analytics database with all required tables."""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))

from analytics.database import AnalyticsDatabase, AIPromptTemplate
from datetime import datetime
import bcrypt

def init_database():
    """Initialize database and create default AI template if needed."""
    print("[INIT] Initializing analytics database...")
    
    # Create database instance (this creates all tables)
    db = AnalyticsDatabase()
    
    print("[INIT] Database tables created/verified")
    
    # Check if we need to create a default AI template
    templates = db.list_prompt_templates()
    
    if len(templates) == 0:
        print("[INIT] Creating default AI template...")
        
        default_template = AIPromptTemplate(
            name="Default Gaming Template",
            prompt_text="""You are a social media expert creating engaging content for gaming videos.

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
}""",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add_prompt_template(default_template)
        print("[INIT] Default AI template created and activated")
    else:
        print(f"[INIT] Found {len(templates)} existing AI template(s)")
    
    # Check if we need to create a default admin user
    admin_user = db.get_user_by_username("admin")
    
    if not admin_user:
        print("[INIT] Creating default admin user...")
        
        # Hash the password "admin" with bcrypt
        password = "admin"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        admin_id = db.create_user(
            username="admin",
            email="admin@aio_cc.local",
            password_hash=password_hash,
            role="admin"
        )
        
        print("[INIT] Default admin user created:")
        print("[INIT]   Username: admin")
        print("[INIT]   Password: admin")
        print("[INIT]   Email: admin@aio_cc.local")
        print("[INIT]   Role: admin")
    else:
        print("[INIT] Default admin user already exists")
    
    print("[INIT] Database initialization complete!")

if __name__ == "__main__":
    init_database()

