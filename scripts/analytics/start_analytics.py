#!/usr/bin/env python3
"""Start the analytics API server"""

import uvicorn
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analytics.api_server import app

if __name__ == "__main__":
    print("🚀 Starting Video Analytics API Server")
    print("=" * 50)
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
