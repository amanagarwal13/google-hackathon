"""
Configuration for Flask ADK Agent Server
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # SocketIO settings
    SOCKETIO_ASYNC_MODE = 'threading'  # or 'eventlet' for better performance
    
    # CORS settings
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
    
    # Agent settings
    AGENT_PATH = os.environ.get('AGENT_PATH', './agents/oracle_agent')
    AGENT_TIMEOUT = int(os.environ.get('AGENT_TIMEOUT', 300))  # 5 minutes
    
    # Session settings
    MAX_SESSION_AGE = 24 * 60 * 60  # 24 hours in seconds
    MAX_MESSAGES_PER_SESSION = 1000
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 20))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File upload settings (if needed for agent)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json'}
    
    # Google Cloud settings (using Application Default Credentials like Oracle Agent)
    # Set these environment variables instead of using service account files
    GOOGLE_GENAI_USE_VERTEXAI = os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', 'true').lower() == 'true'
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
    GOOGLE_CLOUD_STORAGE_BUCKET = os.environ.get('GOOGLE_CLOUD_STORAGE_BUCKET')
    
    # Fi MCP settings (if using Oracle agent)
    FI_MCP_URL = os.environ.get('FI_MCP_URL', 'https://fi-mcp-dev-56426154949.us-central1.run.app/mcp/stream')
    
    # Database settings (optional, for persistent storage)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///sessions.db')
    
    # Redis settings (optional, for production)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Override with production values
    SESSION_TYPE = 'redis' if Config.REDIS_URL else 'filesystem'
    SOCKETIO_ASYNC_MODE = 'eventlet'  # Better for production
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    
    # Use in-memory database for tests
    DATABASE_URL = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


def setup_google_cloud_auth():
    """
    Setup Google Cloud authentication using Application Default Credentials
    This replicates the same authentication method used by Oracle Agent
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Set environment variables for ADK agents (same as Oracle Agent)
    if Config.GOOGLE_GENAI_USE_VERTEXAI:
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
    
    if Config.GOOGLE_CLOUD_PROJECT:
        os.environ['GOOGLE_CLOUD_PROJECT'] = Config.GOOGLE_CLOUD_PROJECT
        
    if Config.GOOGLE_CLOUD_LOCATION:
        os.environ['GOOGLE_CLOUD_LOCATION'] = Config.GOOGLE_CLOUD_LOCATION
        
    if Config.GOOGLE_CLOUD_STORAGE_BUCKET:
        os.environ['GOOGLE_CLOUD_STORAGE_BUCKET'] = Config.GOOGLE_CLOUD_STORAGE_BUCKET
    
    # Verify Application Default Credentials are available
    try:
        from google.auth import default
        credentials, project = default()
        logger.info(f"✅ Google Cloud authentication successful. Project: {project}")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Google Cloud authentication not configured: {e}")
        logger.info("Run: gcloud auth application-default login")
        return False 