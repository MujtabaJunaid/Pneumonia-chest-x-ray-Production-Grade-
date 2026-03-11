"""
FastAPI Application - Pneumonia Detection
"""

import os
import shutil
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import SessionLocal, create_tables, get_db
from backend.app.models import Patient, Prediction, AuditLog
from backend.app.schemas import (
    PatientCreate, PatientRead, PatientWithPredictions, PatientUpdate,
    PredictionRead, PredictionResponse, AuditLogRead
)
from backend.app.ml.ml_pipeline import PneumoniaONNXPredictor

# FastAPI app initialization
print("FastAPI Application starting...")

app = FastAPI(
    title="Medical AI for Pneumonia Detection",
    description="Medical AI Application for Pneumonia Detection",
    version="1.0.0"
)

# Configure CORS middleware
print("Configuring CORS middleware...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
predictor: Optional[PneumoniaONNXPredictor] = None
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)
print(f"Upload directory: {UPLOAD_DIR}")


# Startup and Shutdown Events

@app.on_event("startup")
async def startup_event():
    """
    Initialize on application startup:
    - Create database tables
    - Load ML model
    """
    global predictor
    
    print("\n" + "="*60)
    print("Starting application...")
    print("="*60 + "\n")
    
    # Create database tables
    create_tables()
    
    # Load ML predictor
    try:
        print("Loading ML model...")
        predictor = PneumoniaONNXPredictor(
            model_path="backend/app/ml/pneumonia_model.onnx"
        )
        print("ML model loaded successfully\n")
    except FileNotFoundError:
        print("Warning: ML model file not found")
        print("   Please export ONNX model: backend/app/ml/pneumonia_model.onnx\n")
    except Exception as e:
        print(f"Error loading ML model - {str(e)}\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    print("\n" + "="*60)
    print("Shutting down application...")
    print("="*60 + "\n")


# Health check endpoint

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check application health
    """
    return {
        "status": "healthy",
        "message": "Application is running successfully"
    }


# ========================
# Ù…Ø±ÛŒØ¶ Ú©Û’ Ø±ÙˆÙ¹Ø³ (Patient Routes)
# ========================

@app.post("/api/v1/patients/", response_model=PatientRead, tags=["Patients"])
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Ù†ÛŒØ§ Ù…Ø±ÛŒØ¶ Ø´Ø§Ù…Ù„ Ú©Ø±ÛŒÚº
    
    Parameters:
    -----------
    patient : PatientCreate
        Ù…Ø±ÛŒØ¶ Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª
    
    Returns:
    --------
    PatientRead
        Ø¨Ù†Ø§ÛŒØ§ Ú¯ÛŒØ§ Ù…Ø±ÛŒØ¶
    """
    print(f"âž• Ù†ÛŒØ§ Ù…Ø±ÛŒØ¶ Ø´Ø§Ù…Ù„ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’: {patient.name}")
    
    try:
        # Create new patient record
        db_patient = Patient(
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            contact_info=patient.contact_info
        )
        
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        print(f"âœ“ Ù…Ø±ÛŒØ¶ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø´Ø§Ù…Ù„ ÛÙˆÚ¯ÛŒØ§: ID={db_patient.id}")
        
        return db_patient
        
    except Exception as e:
        print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: Ù…Ø±ÛŒØ¶ Ø´Ø§Ù…Ù„ Ú©Ø±ØªÛ’ ÙˆÙ‚Øª - {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ø®Ø±Ø§Ø¨ÛŒ: Ù…Ø±ÛŒØ¶ Ø´Ø§Ù…Ù„ Ú©Ø±Ù†Û’ Ù…ÛŒÚº Ù†Ø§Ú©Ø§Ù…"
        )


@app.get("/api/v1/patients/{patient_id}", response_model=PatientWithPredictions, tags=["Patients"])
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Ù…Ø±ÛŒØ¶ Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø§ÙˆØ± ØªÙ…Ø§Ù… Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒØ§Úº Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
    
    Parameters:
    -----------
    patient_id : int
        Ù…Ø±ÛŒØ¶ Ú©ÛŒ ID
    
    Returns:
    --------
    PatientWithPredictions
        Ù…Ø±ÛŒØ¶ Ø§ÙˆØ± Ø§Ù† Ú©ÛŒ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒØ§Úº
    """
    print(f"ðŸ” Ù…Ø±ÛŒØ¶ Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’: ID={patient_id}")
    
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not db_patient:
        print(f"âŒ Ù…Ø±ÛŒØ¶ Ù†ÛÛŒÚº Ù…Ù„Ø§: ID={patient_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ù…Ø±ÛŒØ¶ Ù†ÛÛŒÚº Ù…Ù„Ø§"
        )
    
    return db_patient


@app.get("/api/v1/patients/", response_model=list[PatientRead], tags=["Patients"])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    ØªÙ…Ø§Ù… Ù…Ø±ÛŒØ¶ÙˆÚº Ú©ÛŒ ÙÛØ±Ø³Øª Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
    
    Parameters:
    -----------
    skip : int
        Ú©ØªÙ†Û’ Ø±ÛŒÚ©Ø§Ø±ÚˆØ² Ú©Ùˆ Ú†Ú¾ÙˆÚ‘ÛŒÚº
    limit : int
        Ú©ØªÙ†Û’ Ø±ÛŒÚ©Ø§Ø±ÚˆØ² ÙˆØ§Ù¾Ø³ Ú©Ø±ÛŒÚº
    
    Returns:
    --------
    list[PatientRead]
        Ù…Ø±ÛŒØ¶ÙˆÚº Ú©ÛŒ ÙÛØ±Ø³Øª
    """
    print(f"ðŸ“‹ Ù…Ø±ÛŒØ¶ÙˆÚº Ú©ÛŒ ÙÛØ±Ø³Øª Ø­Ø§ØµÙ„ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’ (skip={skip}, limit={limit})")
    
    patients = db.query(Patient).offset(skip).limit(limit).all()
    print(f"âœ“ {len(patients)} Ù…Ø±ÛŒØ¶ Ù…Ù„Û’")
    
    return patients


@app.put("/api/v1/patients/{patient_id}", response_model=PatientRead, tags=["Patients"])
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Ù…ÙˆØ¬ÙˆØ¯Û Ù…Ø±ÛŒØ¶ Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø§Ù¾ ÚˆÛŒÙ¹ Ú©Ø±ÛŒÚº
    """
    print(f"âœï¸  Ù…Ø±ÛŒØ¶ Ú©Ùˆ Ø§Ù¾ ÚˆÛŒÙ¹ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’: ID={patient_id}")
    
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ù…Ø±ÛŒØ¶ Ù†ÛÛŒÚº Ù…Ù„Ø§"
        )
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    print(f"âœ“ Ù…Ø±ÛŒØ¶ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø§Ù¾ ÚˆÛŒÙ¹ ÛÙˆÚ¯ÛŒØ§")
    
    return db_patient


# ========================
# Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©Û’ Ø±ÙˆÙ¹Ø³ (Prediction Routes)
# ========================

@app.post("/api/v1/predictions/predict-with-patient", response_model=PredictionResponse, tags=["Predictions"])
async def predict_with_patient(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Ù…Ø±ÛŒØ¶ Ú©Û’ Ù„ÛŒÛ’ X-ray Ú©ÛŒ ØªÙ†Ø¨ÛØ§Øª Ø¯ÛŒÚº Ø§ÙˆØ± Ù†ØªØ§Ø¦Ø¬ Ù…Ø­ÙÙˆØ¸ Ú©Ø±ÛŒÚº
    
    Parameters:
    -----------
    patient_id : int
        Ù…Ø±ÛŒØ¶ Ú©ÛŒ ID
    file : UploadFile
        Ø§Ù¾ Ù„ÙˆÚˆ Ú©ÛŒ Ú¯Ø¦ÛŒ X-ray ÙØ§Ø¦Ù„ (PNG, JPG, DICOM)
    
    Returns:
    --------
    PredictionResponse
        ØªÙ†Ø¨ÛØ§Øª Ú©Û’ Ù†ØªØ§Ø¦Ø¬ (Urdu Ù…ÛŒÚº Ø³Ù¹ÛŒÙ¹Ø³ Ù¾ÛŒØºØ§Ù… Ú©Û’ Ø³Ø§ØªÚ¾)
    """
    print("\n" + "="*60)
    print("ðŸ”¬ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©Û’ Ù„ÛŒÛ’ Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ù…ÙˆØµÙˆÙ„ ÛÙˆØ¦ÛŒ")
    print("="*60)
    
    try:
        # Ù…Ø±ÛŒØ¶ Ú©ÛŒ Ù…ÙˆØ¬ÙˆØ¯Ú¯ÛŒ Ú©ÛŒ Ø¬Ø§Ù†Ú† Ú©Ø±ÛŒÚº
        print(f"ðŸ‘¤ Ù…Ø±ÛŒØ¶ ID {patient_id} Ú©Ùˆ ØªÙ„Ø§Ø´ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’...")
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not db_patient:
            print(f"âŒ Ù…Ø±ÛŒØ¶ Ù†ÛÛŒÚº Ù…Ù„Ø§: ID={patient_id}")
            
            # Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ù…ÛŒÚº Ù†Ø§Ú©Ø§Ù…ÛŒ Ø±ÛŒÚ©Ø§Ø±Úˆ Ú©Ø±ÛŒÚº
            audit_log = AuditLog(
                endpoint_accessed="/api/v1/predictions/predict-with-patient",
                action_details=f"Ù†Ø§Ú©Ø§Ù…: Ù…Ø±ÛŒØ¶ ID {patient_id} Ù†ÛÛŒÚº Ù…Ù„Ø§"
            )
            db.add(audit_log)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ù…Ø±ÛŒØ¶ Ù†ÛÛŒÚº Ù…Ù„Ø§"
            )
        
        # ÙØ§Ø¦Ù„ Ú©Ùˆ Ù…Ø­ÙÙˆØ¸ Ú©Ø±ÛŒÚº
        print(f"ðŸ’¾ ÙØ§Ø¦Ù„ Ù…Ø­ÙÙˆØ¸ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’: {file.filename}")
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"âœ“ ÙØ§Ø¦Ù„ Ù…Ø­ÙÙˆØ¸ ÛÙˆÚ¯Ø¦ÛŒ: {file_path}")
        
        # ML Ù…Ø§ÚˆÙ„ Ø³Û’ ØªÙ†Ø¨ÛØ§Øª Ù„ÛŒÚº
        if predictor is None:
            print("âŒ Ø®Ø±Ø§Ø¨ÛŒ: ML Ù…Ø§ÚˆÙ„ Ù„ÙˆÚˆ Ù†ÛÛŒÚº ÛÛ’")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model Ø§Ø¨Ú¾ÛŒ Ø¯Ø³ØªÛŒØ§Ø¨ Ù†ÛÛŒÚº ÛÛ’"
            )
        
        print(f"ðŸ¤– ML Ù…Ø§ÚˆÙ„ Ø³Û’ ØªÙ†Ø¨ÛØ§Øª Ù„ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛŒÚº...")
        predictions = predictor.predict_from_file(file_path)
        
        # ÚˆÛŒÙ¹Ø§Ø¨ÛŒØ³ Ù…ÛŒÚº Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù…Ø­ÙÙˆØ¸ Ú©Ø±ÛŒÚº
        print(f"ðŸ“Š Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ ÚˆÛŒÙ¹Ø§Ø¨ÛŒØ³ Ù…ÛŒÚº Ù…Ø­ÙÙˆØ¸ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’...")
        db_prediction = Prediction(
            patient_id=patient_id,
            image_path=file_path,
            class_index=predictions["class_index"],
            confidence_score=predictions["confidence_score"],
            inference_time_ms=predictions["inference_time_ms"]
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        print(f"âœ“ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù…Ø­ÙÙˆØ¸ ÛÙˆÚ¯Ø¦ÛŒ: ID={db_prediction.id}")
        
        # Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ù…ÛŒÚº Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø±ÛŒÚ©Ø§Ø±Úˆ Ú©Ø±ÛŒÚº
        print(f"ðŸ“ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ù…ÛŒÚº Ø±ÛŒÚ©Ø§Ø±Úˆ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’...")
        audit_log = AuditLog(
            endpoint_accessed="/api/v1/predictions/predict-with-patient",
            action_details=f"Ù…Ø±ÛŒØ¶ ID {patient_id} Ú©Û’ Ù„ÛŒÛ’ X-ray Ú©Ø§ ØªØ¬Ø²ÛŒÛ Ú©ÛŒØ§ Ú¯ÛŒØ§Û” Ù†ØªÛŒØ¬Û: {predictions['status_message']}, Ø§Ø¹ØªÙ…Ø§Ø¯: {predictions['confidence_score']:.2f}%"
        )
        
        db.add(audit_log)
        db.commit()
        
        print(f"âœ“ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ø±ÛŒÚ©Ø§Ø±Úˆ ÛÙˆÚ¯ÛŒØ§")
        
        # Ø¬ÙˆØ§Ø¨ ØªÛŒØ§Ø± Ú©Ø±ÛŒÚº
        response = PredictionResponse(
            class_index=predictions["class_index"],
            confidence_score=predictions["confidence_score"],
            inference_time_ms=predictions["inference_time_ms"],
            status_message=predictions["status_message"],
            patient_id=patient_id,
            prediction_id=db_prediction.id
        )
        
        print("="*60)
        print(f"âœ… Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ù…Ú©Ù…Ù„ ÛÙˆØ¦ÛŒ")
        print("="*60 + "\n")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù…ÛŒÚº - {str(e)}")
        db.rollback()
        
        # Ù†Ø§Ú©Ø§Ù…ÛŒ Ú©Ùˆ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ù…ÛŒÚº Ø±ÛŒÚ©Ø§Ø±Úˆ Ú©Ø±ÛŒÚº
        try:
            audit_log = AuditLog(
                endpoint_accessed="/api/v1/predictions/predict-with-patient",
                action_details=f"Ø®Ø±Ø§Ø¨ÛŒ: {str(e)}"
            )
            db.add(audit_log)
            db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ"
        )


@app.get("/api/v1/predictions/{prediction_id}", response_model=PredictionRead, tags=["Predictions"])
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    Ù…Ø®ØµÙˆØµ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
    """
    print(f"ðŸ” Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’: ID={prediction_id}")
    
    db_prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not db_prediction:
        print(f"âŒ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù†ÛÛŒÚº Ù…Ù„ÛŒ: ID={prediction_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù†ÛÛŒÚº Ù…Ù„ÛŒ"
        )
    
    return db_prediction


@app.get("/api/v1/patients/{patient_id}/predictions", response_model=list[PredictionRead], tags=["Predictions"])
async def get_patient_predictions(
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Ù…Ø±ÛŒØ¶ Ú©ÛŒ ØªÙ…Ø§Ù… Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒØ§Úº Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
    """
    print(f"ðŸ“‹ Ù…Ø±ÛŒØ¶ ID {patient_id} Ú©ÛŒ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒØ§Úº Ø­Ø§ØµÙ„ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛŒÚº")
    
    # Ù…Ø±ÛŒØ¶ Ú©ÛŒ Ù…ÙˆØ¬ÙˆØ¯Ú¯ÛŒ Ú©ÛŒ Ø¬Ø§Ù†Ú† Ú©Ø±ÛŒÚº
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ù…Ø±ÛŒØ¶ Ù†ÛÛŒÚº Ù…Ù„Ø§"
        )
    
    predictions = db.query(Prediction)\
        .filter(Prediction.patient_id == patient_id)\
        .order_by(desc(Prediction.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    print(f"âœ“ {len(predictions)} Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒØ§Úº Ù…Ù„ÛŒÚº")
    
    return predictions


# ========================
# Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ú©Û’ Ø±ÙˆÙ¹Ø³ (Audit Log Routes)
# ========================

@app.get("/api/v1/audit-logs", response_model=list[AuditLogRead], tags=["Audit"])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    ØªÙ…Ø§Ù… Ø¢ÚˆÙ¹ Ù„Ø§Ú¯Ø² Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
    """
    print(f"ðŸ“‹ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯Ø² Ø­Ø§ØµÙ„ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛŒÚº (skip={skip}, limit={limit})")
    
    audit_logs = db.query(AuditLog)\
        .order_by(desc(AuditLog.timestamp))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    print(f"âœ“ {len(audit_logs)} Ù„Ø§Ú¯Ø² Ù…Ù„Û’")
    
    return audit_logs


@app.get("/api/v1/audit-logs/patient/{patient_id}", response_model=list[AuditLogRead], tags=["Audit"])
async def get_patient_audit_logs(
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Ù…Ø±ÛŒØ¶ Ø³Û’ Ù…ØªØ¹Ù„Ù‚Û Ø¢ÚˆÙ¹ Ù„Ø§Ú¯Ø² Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
    """
    print(f"ðŸ“‹ Ù…Ø±ÛŒØ¶ ID {patient_id} Ú©Û’ Ù„Ø§Ú¯Ø² Ø­Ø§ØµÙ„ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛŒÚº")
    
    audit_logs = db.query(AuditLog)\
        .filter(AuditLog.action_details.contains(f"patient_id {patient_id}" or f"Patient ID {patient_id}" or f"Ù…Ø±ÛŒØ¶ ID {patient_id}"))\
        .order_by(desc(AuditLog.timestamp))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return audit_logs


# ========================
# Root Route
# ========================

@app.get("/", tags=["Root"])
async def read_root():
    """
    Ø±ÙˆÙ¹ì—”Úˆ Ù¾ÙˆØ§Ø¦Ù†Ù¹
    """
    return {
        "message": "Ù¾Ø§Ø¦Ù„Ù…ÙˆÙ†ÛŒØ§ Ú©ÛŒ ØªØ´Ø®ÛŒØµ Ú©Û’ Ù„ÛŒÛ’ Ø·Ø¨ÛŒ Ø°ÛØ§Ù†Øª",
        "app_name": "Medical AI Application",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    print("\nðŸ¥ Ù¾Ø§Ø¦Ù„Ù…ÙˆÙ†ÛŒØ§ Ú©ÛŒ ØªØ´Ø®ÛŒØµ Ú©ÛŒ Ø§ÛŒÙ¾Ù„ÛŒÚ©ÛŒØ´Ù† Ø´Ø±ÙˆØ¹ ÛÙˆ Ø±ÛÛŒ ÛÛ’...")
    print("https://localhost:8000/docs Ù¾Ø± API Ø¯Ø³ØªØ§ÙˆÛŒØ²Ø§Øª Ø¯ÛŒÚ©Ú¾ÛŒÚº\n")
