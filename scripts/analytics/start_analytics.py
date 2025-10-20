#!/usr/bin/env python3
"""Start the analytics API server"""

import uvicorn
import sys
from pathlib import Path

# Add the src directory to the path
src_path = str(Path(__file__).parent.parent.parent / "src")
sys.path.insert(0, src_path)

if __name__ == "__main__":
    print("Starting Video Analytics API Server")
    print("=" * 50)
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Use import string for reload to work
    uvicorn.run(
        "analytics.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
        reload_dirs=[src_path]
    )
