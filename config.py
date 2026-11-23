import os
from pathlib import Path

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent

# Detect Vercel or Serverless Read-Only Filesystem
IS_SERVERLESS = (
    os.environ.get('VERCEL') == '1' or 
    bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME')) or
    os.environ.get('SERVERLESS') == '1'
)

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'banking-fraud-sentinel-defense-key-2026-secure-random')
    
    # Database Configuration (Writable /tmp for serverless, persistent database/ for container)
    if IS_SERVERLESS:
        DB_PATH = Path('/tmp') / 'banking_fraud.db'
        UPLOAD_FOLDER = Path('/tmp') / 'uploads'
        REPORTS_DIR = Path('/tmp') / 'reports_export'
    else:
        DB_PATH = BASE_DIR / 'database' / 'banking_fraud.db'
        UPLOAD_FOLDER = BASE_DIR / 'dataset' / 'uploads'
        REPORTS_DIR = BASE_DIR / 'reports_export'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Configurations
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 Megabytes max CSV size
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Model and Scaler Storage
    MODEL_DIR = BASE_DIR / 'models'
    MODEL_PATH = MODEL_DIR / 'fraud_model.pkl'
    SCALER_PATH = MODEL_DIR / 'scaler.pkl'
    METRICS_PATH = MODEL_DIR / 'model_metrics.json'
    DATASET_PATH = BASE_DIR / 'dataset' / 'creditcard.csv'
    
    # Risk Classification Thresholds
    RISK_THRESHOLDS = {
        'LOW': 0.20,        # < 0.20 -> Low Risk
        'MEDIUM': 0.50,     # 0.20 - 0.499 -> Medium Risk
        'HIGH': 0.80,       # 0.50 - 0.799 -> High Risk
        'CRITICAL': 1.00    # >= 0.80 -> Critical Risk
    }
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Reports Export Directory
    REPORTS_DIR = BASE_DIR / 'reports_export'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Active Configuration Selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
