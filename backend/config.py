"""
Configuration module for MSME Financial Health Score backend.
Loads environment variables and provides configuration constants.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
    
    # Data Adapter Mode: 'mock' or 'production'
    ADAPTER_MODE = os.getenv('ADAPTER_MODE', 'mock')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Model Configuration
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    @staticmethod
    def validate():
        """Validate that required configuration is present."""
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
        missing = [var for var in required_vars if not getattr(Config, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
