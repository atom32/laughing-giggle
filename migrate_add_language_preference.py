#!/usr/bin/env python3
"""
Database migration script to add preferred_language column to User table.

This script adds the preferred_language column to existing User records
and sets the default value to 'en' for all existing users.
"""

import sqlite3
import os
import logging
from config.i18n import detect_browser_language, DEFAULT_LANGUAGE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database(db_path):
    """
    Add preferred_language column to User table if it doesn't exist.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if preferred_language column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'preferred_language' in columns:
            logger.info("preferred_language column already exists, skipping migration")
            return True
        
        logger.info("Adding preferred_language column to User table...")
        
        # Add the preferred_language column with default value
        cursor.execute("""
            ALTER TABLE user 
            ADD COLUMN preferred_language VARCHAR(5) DEFAULT 'en'
        """)
        
        # Update all existing users to have the default language preference
        cursor.execute("""
            UPDATE user 
            SET preferred_language = ? 
            WHERE preferred_language IS NULL
        """, (DEFAULT_LANGUAGE,))
        
        # Commit changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM user WHERE preferred_language IS NOT NULL")
        updated_count = cursor.fetchone()[0]
        
        logger.info(f"Migration completed successfully. Updated {updated_count} user records.")
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Database migration failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


def main():
    """Main migration function."""
    # Database paths to migrate
    db_paths = [
        'instance/farm.db',
        'instance/farm_dev.db'
    ]
    
    success_count = 0
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            logger.info(f"Migrating database: {db_path}")
            if migrate_database(db_path):
                success_count += 1
            else:
                logger.error(f"Failed to migrate database: {db_path}")
        else:
            logger.info(f"Database file not found, skipping: {db_path}")
    
    if success_count > 0:
        logger.info(f"Migration completed for {success_count} database(s)")
    else:
        logger.warning("No databases were migrated")


if __name__ == '__main__':
    main()