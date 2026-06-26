import json
import os
from flask import session

# Cache for translations
_translations_cache = {}

def load_translations(lang_code):
    """Load translations from JSON file"""
    if lang_code in _translations_cache:
        return _translations_cache[lang_code]
    
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    file_path = os.path.join(translations_dir, f'{lang_code}.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations_cache[lang_code] = translations
            return translations
    except FileNotFoundError:
        # Fallback to English
        if lang_code != 'en':
            return load_translations('en')
        return {}

def get_user_language():
    """Get user's selected language from session"""
    return session.get('user_language', 'en')

def set_user_language(lang_code):
    """Set user's language in session"""
    valid_languages = ['en', 'kn', 'te', 'hi', 'ta']
    if lang_code in valid_languages:
        session['user_language'] = lang_code
        return True
    return False

def get_text(key, lang_code=None):
    """Get translated text for a key"""
    if lang_code is None:
        lang_code = get_user_language()
    
    translations = load_translations(lang_code)
    return translations.get(key, key)
