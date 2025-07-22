#!/usr/bin/env python3
"""
Translation extraction script for the Farm Manager application.

This script extracts all translatable strings from Python files and Jinja2 templates
and creates/updates the messages.pot template file.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def extract_translations():
    """Extract translatable strings and create messages.pot file."""
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        logger.info("Extracting translatable strings...")
        
        # Run babel extract command
        cmd = [
            'python', '-m', 'babel.messages.frontend', 'extract',
            '-F', 'babel.cfg',
            '-k', '_l',
            '-o', 'messages.pot',
            '.'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Translation extraction completed successfully")
            logger.info(f"✓ Created/updated messages.pot template file")
            
            # Count extracted strings
            if os.path.exists('messages.pot'):
                with open('messages.pot', 'r', encoding='utf-8') as f:
                    content = f.read()
                    msgid_count = content.count('msgid "') - 1  # Subtract header msgid
                    logger.info(f"✓ Extracted {msgid_count} translatable strings")
            
        else:
            logger.error("✗ Translation extraction failed")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during translation extraction: {e}")
        return False
    
    return True

def main():
    """Main function."""
    logger.info("Starting translation extraction...")
    
    if extract_translations():
        logger.info("Translation extraction completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Review the generated messages.pot file")
        logger.info("2. Update existing translations: python scripts/update_translations.py")
        logger.info("3. Add new languages: python scripts/init_language.py <language_code>")
        sys.exit(0)
    else:
        logger.error("Translation extraction failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()