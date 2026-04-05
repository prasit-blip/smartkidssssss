"""
Configuration settings for the Tutoring School Management System.

Supports multiple environments: development, testing, and production.
All sensitive values should be set via environment variables.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///tutoring_school.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Email settings (for password reset, notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # LINE Notify API (optional)
    LINE_NOTIFY_TOKEN = os.environ.get('LINE_NOTIFY_TOKEN')
    
    # Sentry (Error tracking)
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Application version
    VERSION = '1.0.0'
    
    # Pagination
    POSTS_PER_PAGE = 20
    STUDENTS_PER_PAGE = 20
    COURSES_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tutoring_school_dev.db'
    
    # Disable rate limiting in development
    RATELIMIT_ENABLED = False
    
    # Console logging in development
    LOG_TO_CONSOLE = True


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable rate limiting in testing
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Require PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/tutoring_school'
    
    # Stricter security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Enable rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Logging to file
    LOG_FILE = 'logs/tutoring_school.log'
    LOG_LEVEL = 'INFO'


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
