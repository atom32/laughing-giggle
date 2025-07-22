#!/usr/bin/env python3
"""
Development server startup script for Park Tycoon Game
"""
import asyncio
import logging
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import get_settings
from app.core.logging import setup_logging


def main():
    """Start the development server with proper initialization."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Park Tycoon Game development server...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Host: {settings.host}:{settings.port}")
    logger.info(f"Database: {settings.database_url}")
    
    try:
        # Start the server using uvicorn
        cmd = [
            "uvicorn",
            "main:app",
            "--host", settings.host,
            "--port", str(settings.port),
            "--reload",
            "--log-level", settings.log_level.lower(),
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=project_root)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()