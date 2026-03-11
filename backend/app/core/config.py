"""
Ø§ÛŒÙ¾Ù„ÛŒÚ©ÛŒØ´Ù† Ú©ÛŒ ØªØ±ØªÛŒØ¨ Ø§ÙˆØ± Ù…Ø§Ø­ÙˆÙ„ Ú©ÛŒ ØªØ±ØªÛŒØ¨
Application Configuration and Environment Settings
"""

import os
from dotenv import load_dotenv

# .env ÙØ§Ø¦Ù„ Ù„ÙˆÚˆ Ú©Ø±ÛŒÚº
load_dotenv()


class Settings:
    """
    Ø§ÛŒÙ¾Ù„ÛŒÚ©ÛŒØ´Ù† Ú©ÛŒ ØªØ±ØªÛŒØ¨Ø§Øª Ú©Ù„Ø§Ø³
    """
    
    # ÚˆÛŒÙ¹Ø§Ø¨ÛŒØ³
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./medical_ai.db"
    )
    
    # FastAPI
    API_TITLE: str = "Ù¾Ø§Ø¦Ù„Ù…ÙˆÙ†ÛŒØ§ Ú©ÛŒ ØªØ´Ø®ÛŒØµ Ú©Û’ Ù„ÛŒÛ’ Ø·Ø¨ÛŒ Ø°ÛØ§Ù†Øª"
    API_VERSION: str = "1.0.0"
    
    # Ø³ÛŒÚ©ÛŒÙˆØ±Ù¹ÛŒ
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Ù…Ø§ÚˆÙ„
    MODEL_PATH: str = os.getenv(
        "MODEL_PATH",
        "backend/app/ml/pneumonia_model.onnx"
    )
    
    # ÛÙˆØ³Ù¹
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Ù…Ø§Ø­ÙˆÙ„
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


# Ø³ÛŒÙ¹Ù†Ú¯Ø² Ú©ÛŒ Ù…Ø«Ø§Ù„
settings = Settings()

print(f"""
ðŸ“‹ Ø§ÛŒÙ¾Ù„ÛŒÚ©ÛŒØ´Ù† Ú©ÛŒ ØªØ±ØªÛŒØ¨Ø§Øª:
   - ÚˆÛŒÙ¹Ø§Ø¨ÛŒØ³: {settings.DATABASE_URL}
   - ML Ù…Ø§ÚˆÙ„: {settings.MODEL_PATH}
   - ÛÙˆØ³Ù¹: {settings.HOST}:{settings.PORT}
   - Debug: {settings.DEBUG}
""")
