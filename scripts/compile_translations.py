#!/usr/bin/env python3
"""
Translation compilation script for the Farm Manager application.

This script compiles .po translation files into .mo binary files for runtime use.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def compile_translations():
    """Compile .po files into .mo binary files."""
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        # Check if translations directory exists
        if not os.path.exists('translations'):
            logger.error("✗ translations directory not found.")
            return False
        
        logger.info("Compiling translation files...")
        
        # Run babel compile command
        cmd = [
            'python', '-m', 'babel.messages.frontend', 'compile',
            '-d', 'translations'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Translation compilation completed successfully")
            
            # List compiled languages and check file sizes
            translations_dir = 'translations'
            compiled_count = 0
            
            for lang_dir in os.listdir(translations_dir):
                lang_path = os.path.join(translations_dir, lang_dir)
                if os.path.isdir(lang_path):
                    mo_file = os.path.join(lang_path, 'LC_MESSAGES', 'messages.mo')
                    if os.path.exists(mo_file):
                        file_size = os.path.getsize(mo_file)
                        logger.info(f"✓ Compiled {lang_dir}: {file_size} bytes")
                        compiled_count += 1
            
            logger.info(f"✓ Successfully compiled {compiled_count} language(s)")
            
        else:
            logger.error("✗ Translation compilation failed")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during translation compilation: {e}")
        return False
    
    return True

def main():
    """Main function."""
    logger.info("Starting translation compilation...")
    
    if compile_translations():
        logger.info("Translation compilation completed successfully!")
        logger.info("Translations are now ready for use in the application.")
        sys.exit(0)
    else:
        logger.error("Translation compilation failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()