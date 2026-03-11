#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock Data Generator for Pneumonia AI Detector
Phase 4: Database Population with Pakistani Faker Data

Generates:
- 1,000 Patient records (with Pakistani names and contact info)
- 2,500 Prediction records (randomly distributed)

Uses Faker with ur_PK locale for authentic Pakistan data.
All terminal output in Urdu for localization.
"""

import os
import sys
import random
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Base, Patient, Prediction, AuditLog
from app.database import get_db

# Initialize Faker with Pakistani locale
fake = Faker('ur_PK')

# Urdu messages for terminal output
MESSAGES = {
    'start': 'ðŸš€ ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù…ÛŒÚº ÚˆÛŒÙ¹Ø§ Ø¨Ú¾Ø±Ù†Ø§ Ø´Ø±ÙˆØ¹...',
    'creating_tables': 'ðŸ“Š ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ø¨Ù† Ø±ÛÛ’ ÛÛŒÚº...',
    'tables_created': 'âœ… Ù¹ÛŒØ¨Ù„Ø² Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ù†Ø§Ø¦Û’ Ú¯Ø¦Û’',
    'generating_patients': 'ðŸ‘¥ {count} Ù…Ø±ÛŒØ¶ÙˆÚº Ú©Ø§ ÚˆÛŒÙ¹Ø§ Ø¨Ù† Ø±ÛØ§ ÛÛ’...',
    'patients_created': 'âœ… {count} Ù…Ø±ÛŒØ¶ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø´Ø§Ù…Ù„ Ú©ÛŒÛ’ Ú¯Ø¦Û’',
    'generating_predictions': 'ðŸ”¬ {count} Ù¾ÛŒØ´ÛŒÙ† Ú¯ÙˆØ¦ÛŒÙˆÚº Ú©Ø§ Ø±ÛŒÚ©Ø§Ø±Úˆ Ø¨Ù† Ø±ÛØ§ ÛÛ’...',
    'predictions_created': 'âœ… {count} Ù¾ÛŒØ´ÛŒÙ† Ú¯ÙˆØ¦ÛŒØ§Úº Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø´Ø§Ù…Ù„ Ú©ÛŒ Ú¯Ø¦ÛŒÚº',
    'creating_audit_logs': 'ðŸ“ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯Ø² Ø¨Ù‘Ù† Ø±ÛÛŒ ÛÛŒÚº...',
    'audit_logs_created': 'âœ… {count} Ø¢ÚˆÙ¹ Ù„Ø§Ú¯ Ø§Ù†Ø¯Ø±Ø§Ø¬Ø§Øª Ø´Ø§Ù…Ù„ Ú©ÛŒÛ’ Ú¯Ø¦Û’',
    'database_stats': 'ðŸ“ˆ ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ø§Ø¹Ø¯Ø§Ø¯Ùˆ Ø´Ù…Ø§Ø±:',
    'total_patients': '   â€¢ Ù…Ø±ÛŒØ¶ÛŒÚº: {count}',
    'total_predictions': '   â€¢ Ù¾ÛŒØ´ÛŒÙ† Ú¯ÙˆØ¦ÛŒØ§Úº: {count}',
    'total_audit_logs': '   â€¢ Ø¢ÚˆÙ¹ Ù„Ø§Ú¯Ø²: {count}',
    'completion_time': 'â±ï¸  Ù…Ú©Ù…Ù„ ÙˆÙ‚Øª: {time:.2f} Ø³ÛŒÚ©Ù†Úˆ',
    'success': 'ðŸŽ‰ ØªÙ…Ø§Ù… ÚˆÛŒÙ¹Ø§ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ú¾Ø± Ø¯ÛŒØ§ Ú¯ÛŒØ§!',
    'error': 'âŒ Ø®Ø±Ø§Ø¨ÛŒ: {error}',
    'batch_progress': '   â†³ Batch {batch_num}: {count} Ø±ÛŒÚ©Ø§Ø±ÚˆØ² Ø´Ø§Ù…Ù„ Ú©ÛŒÛ’ Ú¯Ø¦Û’',
}

def get_database_connection():
    """
    Get database connection from environment or use default
    Ensures UTF-8 encoding for PostgreSQL
    """
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
    
    # If using PostgreSQL, parse and adjust URL
    if database_url.startswith('postgresql://'):
        # Ensure utf-8 encoding
        if 'sslmode' not in database_url:
            database_url += '?sslmode=disable'
    
    return create_engine(database_url, echo=False)

def create_database_tables(engine):
    """
    Create database tables if they don't exist
    ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ø¨Ù†Ø§Ø¦ÛŒÚº
    """
    print(MESSAGES['creating_tables'])
    Base.metadata.create_all(bind=engine)
    print(MESSAGES['tables_created'])

def generate_patients(session, count=1000):
    """
    Generate and insert fake patient records
    Ù…Ø±ÛŒØ¶ÙˆÚº Ú©Ø§ ÚˆÛŒÙ¹Ø§ Ø¨Ù†Ø§Ø¦ÛŒÚº Ø§ÙˆØ± ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù…ÛŒÚº ÚˆØ§Ù„ÛŒÚº
    """
    print(f"\n{MESSAGES['generating_patients'].format(count=count)}")
    
    patients = []
    batch_size = 100
    
    for i in range(count):
        # Generate Pakistani name and contact info
        patient = Patient(
            name=fake.name(),          # Pakistani name
            age=random.randint(18, 85),
            gender=random.choice(['M', 'F']),
            contact_info=fake.phone_number(),  # Pakistani phone format
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365))
        )
        patients.append(patient)
        
        # Batch insert for performance
        if (i + 1) % batch_size == 0:
            session.add_all(patients)
            session.commit()
            print(MESSAGES['batch_progress'].format(batch_num=(i + 1) // batch_size, count=batch_size))
            patients = []
    
    # Insert remaining patients
    if patients:
        session.add_all(patients)
        session.commit()
        print(MESSAGES['batch_progress'].format(batch_num=(count + batch_size - 1) // batch_size, count=len(patients)))
    
    print(MESSAGES['patients_created'].format(count=count))
    return count

def generate_predictions(session, patient_count, prediction_count=2500):
    """
    Generate and insert fake prediction records
    Ù¾ÛŒØ´ÛŒÙ† Ú¯ÙˆØ¦ÛŒÙˆÚº Ú©Ø§ ÚˆÛŒÙ¹Ø§ Ø¨Ù†Ø§Ø¦ÛŒÚº
    """
    print(f"\n{MESSAGES['generating_predictions'].format(count=prediction_count)}")
    
    predictions = []
    batch_size = 250
    
    # Get list of patient IDs
    patient_ids = session.query(Patient.id).all()
    patient_ids = [pid[0] for pid in patient_ids]
    
    for i in range(prediction_count):
        # Randomly select a patient
        patient_id = random.choice(patient_ids)
        
        # Generate prediction data
        class_index = random.choice([0, 1])  # 0=Normal, 1=Pneumonia
        
        # Realistic confidence scores
        if class_index == 0:
            # Normal cases: typically high confidence
            confidence = random.uniform(85.0, 99.5)
        else:
            # Pneumonia cases: varies more
            confidence = random.uniform(60.0, 99.0)
        
        prediction = Prediction(
            patient_id=patient_id,
            image_path=f"/uploads/xray_{i}.jpg",
            class_index=class_index,
            confidence_score=round(confidence, 2),
            inference_time_ms=random.randint(100, 300),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365))
        )
        predictions.append(prediction)
        
        # Batch insert for performance
        if (i + 1) % batch_size == 0:
            session.add_all(predictions)
            session.commit()
            print(MESSAGES['batch_progress'].format(batch_num=(i + 1) // batch_size, count=batch_size))
            predictions = []
    
    # Insert remaining predictions
    if predictions:
        session.add_all(predictions)
        session.commit()
        print(MESSAGES['batch_progress'].format(batch_num=(prediction_count + batch_size - 1) // batch_size, count=len(predictions)))
    
    print(MESSAGES['predictions_created'].format(count=prediction_count))
    return prediction_count

def generate_audit_logs(session, prediction_count):
    """
    Generate and insert audit log records based on predictions
    Ø¢ÚˆÙ¹ Ù„Ø§Ú¯Ø² Ø¨Ù†Ø§Ø¦ÛŒÚº
    """
    print(f"\n{MESSAGES['creating_audit_logs']}")
    
    audit_logs = []
    
    # Create audit logs for data generation
    audit_log = AuditLog(
        endpoint_accessed='/api/v1/predictions/predict-with-patient',
        action_details=f'Mock data generation: Created {prediction_count} predictions',
        timestamp=datetime.utcnow()
    )
    audit_logs.append(audit_log)
    
    session.add_all(audit_logs)
    session.commit()
    
    audit_count = len(audit_logs)
    print(MESSAGES['audit_logs_created'].format(count=audit_count))
    return audit_count

def print_database_stats(session, patient_count, prediction_count, audit_count):
    """
    Print final database statistics
    ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ú©Û’ Ø§Ø¹Ø¯Ø§Ø¯Ùˆ Ø´Ù…Ø§Ø± Ø¯Ú©Ú¾Ø§Ø¦ÛŒÚº
    """
    print(f"\n{MESSAGES['database_stats']}")
    print(MESSAGES['total_patients'].format(count=patient_count))
    print(MESSAGES['total_predictions'].format(count=prediction_count))
    print(MESSAGES['total_audit_logs'].format(count=audit_count))

def main():
    """
    Main function to orchestrate data generation
    ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù…ÛŒÚº ÚˆÛŒÙ¹Ø§ Ø¨Ú¾Ø±Ù†Û’ Ú©Ø§ Ù‚Ø±ÛŒÛ Ú©Ø§Ø±
    """
    try:
        print(f"\n{MESSAGES['start']}\n")
        
        # Record start time
        start_time = time.time()
        
        # Get database connection
        engine = get_database_connection()
        
        # Create tables
        create_database_tables(engine)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # Generate mock data
            patient_count = generate_patients(session, count=1000)
            prediction_count = generate_predictions(session, patient_count, prediction_count=2500)
            audit_count = generate_audit_logs(session, prediction_count)
            
            # Print statistics
            print_database_stats(session, patient_count, prediction_count, audit_count)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            print(f"\n{MESSAGES['completion_time'].format(time=execution_time)}")
            print(f"\n{MESSAGES['success']}\n")
            
        finally:
            session.close()
    
    except Exception as e:
        print(f"\n{MESSAGES['error'].format(error=str(e))}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
