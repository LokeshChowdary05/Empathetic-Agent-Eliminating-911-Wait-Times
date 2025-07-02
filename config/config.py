import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///emergency_calls.db")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Emergency Response Settings
    MAX_RESPONSE_TIME = 30  # seconds
    EMPATHY_THRESHOLD = 0.3  # sentiment threshold for empathy trigger
    CRITICAL_KEYWORDS = [
        "unconscious", "not breathing", "bleeding", "chest pain",
        "heart attack", "stroke", "fire", "gun", "assault"
    ]
    
    # Model Settings
    DEFAULT_MODEL = "gpt-3.5-turbo"
    BACKUP_MODEL = "microsoft/DialoGPT-medium"
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # Safety Filters
    PROFANITY_FILTER = True
    MAX_CONVERSATION_TURNS = 50
    SAFETY_KEYWORDS = ["suicide", "self-harm", "overdose"]
    
    # Mock 911 Dispatch
    MOCK_DISPATCH_URL = "http://localhost:8001/dispatch"
    REAL_DISPATCH_ENABLED = False

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = "sqlite:///dev_emergency_calls.db"

class ProductionConfig(Config):
    DEBUG = False
    # Add production-specific settings here

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
