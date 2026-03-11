"""
SQLAlchemy Database Models - HIPAA Compliant
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Patient(Base):
    """
    Patient model with HIPAA compliance
    """
    
    __tablename__ = "patients"
    
    # Ø§ÛÙ… Ú©Ø§Ù„Ù…Ø²
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # M/F/Other
    contact_info = Column(String(255), nullable=True)  # Phone or email
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):

        return f"<Patient(id={self.id}, name={self.name}, age={self.age})>"


class Prediction(Base):
    """
    Prediction model for X-ray analysis results
    """
    
    __tablename__ = "predictions"
    
    # Primary key and foreign key
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    image_path = Column(String(512), nullable=False)  # X-ray file path
    class_index = Column(Integer, nullable=False)  # 0: Normal, 1: Pneumonia
    confidence_score = Column(Float, nullable=False)  # Confidence 0-100
    inference_time_ms = Column(Integer, nullable=False)  # Inference time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")
    
    def __repr__(self):

        return f"<Prediction(id={self.id}, patient_id={self.patient_id}, class={self.class_index})>"


class AuditLog(Base):
    """
    Audit log for all operations - required for HIPAA compliance
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    endpoint_accessed = Column(String(255), nullable=False)  # Example: /api/v1/predictions
    action_details = Column(Text, nullable=False)  # Details: patient ID, file name, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):

        return f"<AuditLog(id={self.id}, endpoint={self.endpoint_accessed}, time={self.timestamp})>"
