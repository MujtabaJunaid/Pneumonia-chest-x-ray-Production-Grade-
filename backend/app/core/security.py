"""
Ø³ÛŒÚ©ÛŒÙˆØ±Ù¹ÛŒ Ø§ÙˆØ± JWT Ú©ÛŒ ØªØ±ØªÛŒØ¨
Security and JWT Configuration
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Ù¾Ø§Ø³ ÙˆØ±Úˆ ÛÛŒØ´Ù†Ú¯ Ú©Ø³Ø§Ø¯Øª
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Ú©ÛŒ ØªØ±ØªÛŒØ¨
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Ù¾Ø§Ø³ ÙˆØ±Úˆ Ú©ÛŒ ØªØµØ¯ÛŒÙ‚ Ú©Ø±ÛŒÚº
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Ù¾Ø§Ø³ ÙˆØ±Úˆ Ú©Ùˆ ÛÛŒØ´ Ú©Ø±ÛŒÚº
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    JWT Ù¹ÙˆÚ©Ù† Ø¨Ù†Ø§Ø¦ÛŒÚº
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
