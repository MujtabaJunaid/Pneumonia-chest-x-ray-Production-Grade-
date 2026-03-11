"""

Pydantic Schemas - Data Validation and Serialization
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Patient schemas

class PatientCreate(BaseModel):
    """
    Schema for creating a new patient
    """
    name: str = Field(..., min_length=1, max_length=255)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., pattern="^(M|F|Other)$")
    contact_info: Optional[str] = Field(None, max_length=255)


class PatientRead(BaseModel):
    """
    Schema for reading patient information
    """
    id: int
    name: str
    age: int
    gender: str
    contact_info: Optional[str]
    created_at: datetime
    
    class Config:
        # Pydantic V2 Ù…ÛŒÚº: from_attributes = True
        # Pydantic V1 Ù…ÛŒÚº: orm_mode = True
        from_attributes = True


class PatientWithPredictions(BaseModel):
    """
    Schema for patient with all associated predictions
    """
    id: int
    name: str
    age: int
    gender: str
    contact_info: Optional[str]
    created_at: datetime
    predictions: List['PredictionRead'] = []
    
    class Config:
        from_attributes = True


# Prediction schemas

class PredictionCreate(BaseModel):
    """
    Schema for saving a new prediction to database
    """
    patient_id: int
    image_path: str = Field(..., max_length=512)
    class_index: int = Field(..., ge=0, le=1)
    confidence_score: float = Field(..., ge=0, le=100)
    inference_time_ms: int = Field(..., ge=0)


class PredictionRead(BaseModel):
    """
    Schema for reading prediction information
    """
    id: int
    patient_id: int
    image_path: str
    class_index: int
    confidence_score: float
    inference_time_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionWithPatient(BaseModel):
    """
    Schema for prediction with associated patient information
    """
    id: int
    patient_id: int
    patient: PatientRead
    image_path: str
    class_index: int
    confidence_score: float
    inference_time_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========================
# Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©Ø§ Ø¬ÙˆØ§Ø¨ (Prediction Response)
# ========================

class PredictionResponse(BaseModel):
    """
    Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©Û’ Ø¬ÙˆØ§Ø¨ Ù…ÛŒÚº Ø§ÛÙ… Ù…Ø¹Ù„ÙˆÙ…Ø§Øª
    ML pipeline Ú©Û’ Ù†ØªØ§Ø¦Ø¬ Ú©Û’ Ø³Ø§ØªÚ¾
    """
    class_index: int = Field(..., description="0: Ù†Ø§Ø±Ù…Ù„ØŒ 1: Ù†Ù…ÙˆÙ†ÛŒØ§")
    confidence_score: float = Field(..., description="Ø§Ø¹ØªÙ…Ø§Ø¯ Ú©ÛŒ ÙÛŒØµØ¯ (0-100)")
    inference_time_ms: int = Field(..., description="Ø§Ù†Ø¯Ø±Ø§Ø² Ù„Ú¯Ø§Ù†Û’ Ú©Ø§ ÙˆÙ‚Øª Ù…Ù„ÛŒ Ø³ÛŒÚ©Ù†Úˆ Ù…ÛŒÚº")
    status_message: str = Field(..., description="Ø§Ø±Ø¯Ùˆ Ù…ÛŒÚº Ø­Ø§Ù„Øª Ú©Ø§ Ù¾ÛŒØºØ§Ù…")
    patient_id: int
    prediction_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "class_index": 1,
                "confidence_score": 92.45,
                "inference_time_ms": 145,
                "status_message": "Ù†Ù…ÙˆÙ†ÛŒØ§ Ú©Ø§ Ø´Ø¨Û",
                "patient_id": 1,
                "prediction_id": 5
            }
        }


# ========================
# Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ø³Ú©ÛŒÙ…Ø§Ø²
# ========================

class AuditLogCreate(BaseModel):
    """
    Ù†ÛŒØ§ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ø±ÛŒÚ©Ø§Ø±Úˆ Ø¨Ù†Ø§Ù†Û’ Ú©Û’ Ù„ÛŒÛ’ Ø³Ú©ÛŒÙ…Ø§
    """
    endpoint_accessed: str
    action_details: str


class AuditLogRead(BaseModel):
    """
    Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ù¾Ú‘Ú¾Ù†Û’ Ú©Û’ Ù„ÛŒÛ’ Ø³Ú©ÛŒÙ…Ø§
    """
    id: int
    endpoint_accessed: str
    action_details: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ========================
# Ø§Ù¾ ÚˆÛŒÙ¹ Ù…Ø§ÚˆÙ„Ø²
# ========================

class PatientUpdate(BaseModel):
    """
    Ù…ÙˆØ¬ÙˆØ¯Û Ù…Ø±ÛŒØ¶ Ú©Ùˆ Ø§Ù¾ ÚˆÛŒÙ¹ Ú©Ø±Ù†Û’ Ú©Û’ Ù„ÛŒÛ’ - ØªÙ…Ø§Ù… ÙÛŒÙ„ÚˆØ² Ø§Ø®ØªÛŒØ§Ø±ÛŒ
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(M|F|Other)$")
    contact_info: Optional[str] = Field(None, max_length=255)
