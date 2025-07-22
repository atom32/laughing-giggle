#!/usr/bin/env python3
"""
New language initialization script for the Farm Manager application.

This script initializes translation files for a new language.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def init_language(language_code):
    """Initialize translation files for a new language."""
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        # Check if messages.pot exists
        if not os.path.exists('messages.pot'):
            logger.error("✗ messages.pot not found. Run extract_translations.py first.")
            return False
        
        # Validate language code
        if not language_code or len(language_code) != 2:
            logger.error("✗ Invalid language code. Please provide a 2-letter language code (e.g., 'de', 'zh').")
            return False
        
        # Check if language already exists
        lang_dir = os.path.join('translations', language_code)
        if os.path.exists(lang_dir):
            logger.warning(f"⚠ Language '{language_code}' already exists. Use update_translations.py to update it.")
            return False
        
        logger.info(f"Initializing translation files for language: {language_code}")
        
        # Run babel init command
        cmd = [
            'python', '-m', 'babel.messages.frontend', 'init',
            '-i', 'messages.pot',
            '-d', 'translations',
            '-l', language_code
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ Successfully initialized translation files for '{language_code}'")
            
            # Check created files
            po_file = os.path.join(lang_dir, 'LC_MESSAGES', 'messages.po')
            if os.path.exists(po_file):
                logger.info(f"✓ Created: {po_file}")
                
                # Count strings to translate
                with open(po_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    msgid_count = content.count('msgid "') - 1  # Subtract header msgid
                    logger.info(f"✓ Ready to translate {msgid_count} strings")
            
        else:
            logger.error(f"✗ Failed to initialize language '{language_code}'")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during language initialization: {e}")
        return False
    
    return True

def main():
    """Main function."""
    if len(sys.argv) != 2:
        logger.error("Usage: python scripts/init_language.py <language_code>")
        logger.error("Example: python scripts/init_language.py de")
        sys.exit(1)
    
    language_code = sys.argv[1].lower()
    
    logger.info(f"Starting language initialization for: {language_code}")
    
    if init_language(language_code):
        logger.info("Language initialization completed successfully!")
        logger.info("Next steps:")
        logger.info(f"1. Edit translations/{language_code}/LC_MESSAGES/messages.po")
        logger.info(f"2. Add '{language_code}' to SUPPORTED_LANGUAGES in config/i18n.py")
        logger.info("3. Update available_languages in config/settings.ini")
        logger.info("4. Compile translations: python scripts/compile_translations.py")
        sys.exit(0)
    else:
        logger.error("Language initialization failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()