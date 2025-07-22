#!/usr/bin/env python3
"""
Database initialization script for Park Tycoon Game
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import get_settings
from app.core.database import init_database
from app.core.logging import setup_logging


async def main():
    """Initialize the database with tables and default data."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting database initialization...")
    
    try:
        await init_database()
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())