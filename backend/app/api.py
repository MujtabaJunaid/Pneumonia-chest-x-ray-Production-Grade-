"""
API Ø±ÙˆÙ¹Ø±Ø² Ú©Û’ Ø§ÛŒÚ© Ø¬Ú¯Û Ø¨ÛŒÚ© ÙˆÙ‚Øª Ø§Ø³ØªØ¹Ù…Ø§Ù„ Ú©Û’ Ù„ÛŒÛ’
API Routers - Centralized Route Management
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

# Ø±ÙˆÙ¹Ø± Ø¨Ù†Ø§Ø¦ÛŒÚº (Ø¶Ø±ÙˆØ±Øª Ú©Û’ Ù…Ø·Ø§Ø¨Ù‚ Ø±ÙˆÙ¹Ø³ Ø´Ø§Ù…Ù„ Ú©Ø±ÛŒÚº)
router = APIRouter(prefix="/api/v1", tags=["API v1"])

# ÛŒÛØ§Úº Ø±ÙˆÙ¹Ø³ Ø´Ø§Ù…Ù„ Ú©Ø±ÛŒÚº (Ø§Ú¯Ø± Ø§Ù„Ú¯ ÙØ§Ø¦Ù„ÙˆÚº Ù…ÛŒÚº ÛÙˆÚº ØªÙˆ)
# Ù…Ø«Ø§Ù„:
# from backend.app.routes import patients, predictions
# router.include_router(patients.router)
# router.include_router(predictions.router)

print("âœ“ API Ø±ÙˆÙ¹Ø±Ø² Ø´Ø§Ù…Ù„ Ú©ÛŒÛ’ Ú¯Ø¦Û’")
