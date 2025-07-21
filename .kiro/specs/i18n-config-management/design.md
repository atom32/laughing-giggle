# Design Document

## Overview

This design implements internationalization (i18n) support using Flask-Babel and centralized configuration management using Python's configparser module with INI files. The solution will externalize all user-facing strings into translation files and move configuration values from hardcoded values in the application to external INI files that can be environment-specific.

## Architecture

### I18n Architecture
- **Flask-Babel Integration**: Use Flask-Babel extension for translation management
- **Translation Files**: Store translations in `.po` files under `translations/` directory
- **Language Detection**: Implement browser language detection with user preference override
- **Template Integration**: Use Babel's template functions (`_()`, `gettext()`) in Jinja2 templates
- **Message Extraction**: Use Babel's extraction tools to automatically find translatable strings

### Configuration Architecture
- **INI File Structure**: Use hierarchical INI files with environment sections
- **Configuration Loader**: Create a centralized configuration class that loads and validates settings
- **Environment Detection**: Detect environment through environment variables or command-line arguments
- **Default Fallbacks**: Provide sensible defaults for all configuration values

## Components and Interfaces

### 1. Translation Management Component

**Files:**
- `babel.cfg` - Babel configuration for string extraction
- `translations/` - Directory containing language-specific translation files
- `config/i18n.py` - I18n configuration and utilities

**Key Functions:**
```python
def get_locale():
    """Determine user's preferred locale"""
    
def init_babel(app):
    """Initialize Babel with Flask app"""
    
def get_available_languages():
    """Return list of available language codes"""
```

### 2. Configuration Management Component

**Files:**
- `config/settings.ini` - Main configuration file
- `config/config.py` - Configuration loader class
- `config/defaults.py` - Default configuration values

**Configuration Structure:**
```ini
[DEFAULT]
# Default settings that apply to all environments

[development]
# Development-specific overrides

[production]
# Production-specific overrides

[testing]
# Testing-specific overrides
```

**Key Classes:**
```python
class AppConfig:
    """Centralized configuration management"""
    def __init__(self, environment=None)
    def get(self, section, key, fallback=None)
    def get_database_uri(self)
    def get_secret_key(self)
```

### 3. Language Selection Interface

**Template Components:**
- Language selector dropdown in navigation/profile
- Language preference form in user profile
- Language detection and storage in user session

**Route Handlers:**
```python
@app.route('/set_language/<language>')
def set_language(language):
    """Set user's language preference"""
```

## Data Models

### User Model Extensions
```python
class User(db.Model):
    # ... existing fields ...
    preferred_language = db.Column(db.String(5), default='en')
```

### Configuration Data Structure
```python
# Configuration sections and their expected keys
CONFIG_SCHEMA = {
    'database': ['uri', 'track_modifications'],
    'security': ['secret_key', 'password_salt'],
    'application': ['debug', 'host', 'port'],
    'game': ['starting_coins', 'starting_farm_size', 'max_level'],
    'i18n': ['default_language', 'available_languages']
}
```

## Error Handling

### Translation Errors
- **Missing Translation**: Fall back to English, log warning
- **Invalid Language Code**: Default to English, show user message
- **Translation File Corruption**: Use cached translations, alert administrator

### Configuration Errors
- **Missing INI File**: Create default file, continue with defaults
- **Invalid Configuration Values**: Use defaults, log warnings
- **Environment Detection Failure**: Default to 'development' environment

### Implementation Error Handling
```python
def safe_translate(key, **kwargs):
    """Safely translate a key with fallback handling"""
    try:
        return gettext(key, **kwargs)
    except Exception as e:
        logger.warning(f"Translation failed for key '{key}': {e}")
        return key  # Return the key itself as fallback
```

## Testing Strategy

### Unit Tests
- **Translation Loading**: Test translation file loading and fallback behavior
- **Configuration Loading**: Test INI file parsing and environment detection
- **Language Detection**: Test browser language detection logic
- **User Preference Storage**: Test language preference persistence

### Integration Tests
- **End-to-End Language Switching**: Test complete language change workflow
- **Configuration Override**: Test environment-specific configuration loading
- **Template Rendering**: Test translated content rendering in templates
- **Database Integration**: Test user language preference storage and retrieval

### Test Data
- **Sample Translation Files**: Create test translations for multiple languages
- **Test Configuration Files**: Create test INI files for different scenarios
- **Mock User Data**: Create test users with different language preferences

### Testing Approach
```python
class I18nTestCase(unittest.TestCase):
    def test_language_detection(self):
        """Test browser language detection"""
        
    def test_translation_fallback(self):
        """Test fallback to English when translation missing"""
        
    def test_user_language_preference(self):
        """Test user language preference storage and retrieval"""

class ConfigTestCase(unittest.TestCase):
    def test_config_loading(self):
        """Test configuration file loading"""
        
    def test_environment_detection(self):
        """Test environment-specific configuration"""
        
    def test_default_fallbacks(self):
        """Test fallback to defaults when config missing"""
```

## Implementation Notes

### Flask-Babel Setup
- Install Flask-Babel: `pip install Flask-Babel`
- Configure Babel in application factory
- Set up locale selector function
- Initialize Babel with app context

### Translation Workflow
1. Mark strings for translation using `_()` or `gettext()`
2. Extract strings: `pybabel extract -F babel.cfg -o messages.pot .`
3. Create language files: `pybabel init -i messages.pot -d translations -l es`
4. Update translations: `pybabel update -i messages.pot -d translations`
5. Compile translations: `pybabel compile -d translations`

### Configuration Migration Strategy
1. Create default INI file with current hardcoded values
2. Update application factory to use configuration loader
3. Replace hardcoded values throughout codebase
4. Add environment detection and override capability
5. Document configuration options for administrators

### Security Considerations
- Store sensitive values (secret keys, database passwords) in environment variables
- Document which configuration values should not be committed to version control
- Implement configuration validation to prevent security misconfigurations
- Use secure defaults for all security-related settings