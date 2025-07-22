#!/usr/bin/env python3
"""
Translation update script for the Farm Manager application.

This script updates existing translation files with new strings from the messages.pot template.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def update_translations():
    """Update existing translation files with new strings."""
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        # Check if messages.pot exists
        if not os.path.exists('messages.pot'):
            logger.error("✗ messages.pot not found. Run extract_translations.py first.")
            return False
        
        logger.info("Updating existing translation files...")
        
        # Run babel update command
        cmd = [
            'python', '-m', 'babel.messages.frontend', 'update',
            '-i', 'messages.pot',
            '-d', 'translations'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Translation update completed successfully")
            
            # List updated languages
            translations_dir = 'translations'
            if os.path.exists(translations_dir):
                languages = [d for d in os.listdir(translations_dir) 
                           if os.path.isdir(os.path.join(translations_dir, d))]
                logger.info(f"✓ Updated translations for languages: {', '.join(languages)}")
            
        else:
            logger.error("✗ Translation update failed")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during translation update: {e}")
        return False
    
    return True

def main():
    """Main function."""
    logger.info("Starting translation update...")
    
    if update_translations():
        logger.info("Translation update completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Review and translate new strings in .po files")
        logger.info("2. Compile translations: python scripts/compile_translations.py")
        sys.exit(0)
    else:
        logger.error("Translation update failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()