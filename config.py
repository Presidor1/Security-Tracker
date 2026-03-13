"""
Configuration Settings for Security Tracker
"""

import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask Configuration
class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'security-tracker-secret-key-2024-change-in-production'
    
    # Database
    DATABASE = os.path.join(BASE_DIR, 'security_tracker.db')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    FACES_FOLDER = os.path.join(BASE_DIR, 'static', 'faces')
    RESULTS_FOLDER = os.path.join(BASE_DIR, 'static', 'results')
    
    # File upload limits
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
    ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS)
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Face recognition settings
    FACE_DETECTION_MODEL = 'hog'  # 'hog' or 'cnn'
    FACE_ENCODING_MODEL = 'small'  # 'small' or 'large'
    FACE_MATCH_TOLERANCE = 0.6  # Lower is more strict
    
    # Analysis settings
    MAX_VIDEO_FRAMES = 10  # Maximum frames to extract from video
    VIDEO_FRAME_INTERVAL = 30  # Extract every Nth frame
    
    # Social media search settings
    SOCIAL_SEARCH_ENABLED = True
    MAX_SOCIAL_RESULTS = 10
    SOCIAL_SEARCH_TIMEOUT = 30  # seconds
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(BASE_DIR, 'security_tracker.log')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # API settings
    API_RATE_LIMIT = '100 per hour'
    API_TIMEOUT = 30

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'
    
    # Use environment variable for secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Stricter rate limiting in production
    API_RATE_LIMIT = '50 per hour'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE = ':memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Get current configuration
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
