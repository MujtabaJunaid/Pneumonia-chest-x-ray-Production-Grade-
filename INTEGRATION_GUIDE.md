# ðŸ”— Phase 1 + Phase 2 Integration Guide

## Overview

You now have a **complete backend stack** ready to run:

```
Phase 1 (ML Pipeline)  â†’  Phase 2 (FastAPI)  â†’  Frontend (Phase 3)
    âœ… DONE                  âœ… DONE               â³ NEXT
```

---

## ðŸ“‹ Files Checklist

### Phase 1 Files (ML Pipeline)
```
backend/app/ml/
â”œâ”€â”€ ml_pipeline.py           âœ… PneumoniaModel, export_to_onnx, PneumoniaONNXPredictor
â”œâ”€â”€ __init__.py              âœ… Package marker
â””â”€â”€ pneumonia_model.onnx     â³ Placeholder (generate by exporting model)
```

### Phase 2 Files (FastAPI Backend)
```
backend/app/
â”œâ”€â”€ main.py                  âœ… FastAPI app + routes
â”œâ”€â”€ models.py                âœ… SQLAlchemy ORM (Patient, Prediction, AuditLog)
â”œâ”€â”€ schemas.py               âœ… Pydantic validation
â”œâ”€â”€ database.py              âœ… DB connection + sessions
â”œâ”€â”€ api.py                   âœ… Router aggregator
â”œâ”€â”€ __init__.py              âœ… Package marker
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ security.py          âœ… JWT + bcrypt
â”‚   â”œâ”€â”€ config.py            âœ… Settings from .env
â”‚   â””â”€â”€ __init__.py          âœ… Package marker
â””â”€â”€ ml/
    â”œâ”€â”€ ml_pipeline.py       âœ… Phase 1 ML code
    â””â”€â”€ __init__.py          âœ… Package marker

backend/
â”œâ”€â”€ requirements.txt         âœ… All dependencies
â””â”€â”€ app/                     âœ… (see above)

root/
â”œâ”€â”€ .env.example             âœ… Environment template
â”œâ”€â”€ PHASE_2_COMPLETE.md      âœ… What's new
â””â”€â”€ ... other root files
```

---

## ðŸš€ Quick Start (5 Steps)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Installs:** fastapi, uvicorn, sqlalchemy, torch, onnxruntime, pydantic, jwt, bcrypt, etc.

### Step 2: Setup Environment
```bash
cd ..
cp .env.example .env
# Edit .env with your settings (optional for SQLite testing)
```

### Step 3: Generate ONNX Model (if needed)
```python
# In Python shell or script:
from backend.app.ml.ml_pipeline import PneumoniaModel, export_to_onnx

model = PneumoniaModel()
export_to_onnx(model, output_path="backend/app/ml/pneumonia_model.onnx")
```

### Step 4: Run FastAPI
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
ðŸš€ FastAPI Ø§ÛŒÙ¾Ù„ÛŒÚ©ÛŒØ´Ù† Ø´Ø±ÙˆØ¹ ÛÙˆ Ø±ÛÛŒ ÛÛ’...
ðŸ”’ CORS middleware Ú©Ùˆ ØªØ±ØªÛŒØ¨ Ø¯ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’...
ðŸ“ Ø§Ù¾ Ù„ÙˆÚˆ ÚˆÛŒØ±ÛŒÚ©Ù¹Ø±ÛŒ: uploads

âš¡ Ø§ÛŒÙ¾Ù„ÛŒÚ©ÛŒØ´Ù† Ø´Ø±ÙˆØ¹ ÛÙˆ Ø±ÛÛŒ ÛÛ’...
ðŸ“ ÚˆÛŒÙ¹Ø§Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ø¨Ù†Ø§Ø¦Û’ Ø¬Ø§ Ø±ÛÛ’ ÛÛŒÚº...
âœ“ Ù¹ÛŒØ¨Ù„Ø² Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ù†Ø§Ø¦Û’ Ú¯Ø¦Û’
ðŸ¤– ML Ù…Ø§ÚˆÙ„ Ù„ÙˆÚˆ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’...
âœ“ ML Ù…Ø§ÚˆÙ„ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ù„ÙˆÚˆ ÛÙˆÚ¯ÛŒØ§

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Test the API
```bash
# Option A: Browser
http://localhost:8000/docs

# Option B: cURL
curl http://localhost:8000/health

# Option C: Python requests
python test_api.py
```

---

## ðŸ”„ Data Flow: From Upload to Response

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    Frontend (React)                          â”‚
â”‚                                                               â”‚
â”‚  1. User selects X-ray file (PNG/JPG/DICOM)                â”‚
â”‚  2. User enters Patient ID                                  â”‚
â”‚  3. Submit form â†’ POST /api/v1/predictions/predict-with-patient
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
                           â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    FastAPI Backend                            â”‚
â”‚                                                               â”‚
â”‚  1. Receive file upload + patient_id                        â”‚
â”‚  2. Validate patient exists (check Patient table)           â”‚
â”‚  3. Save file to disk (/uploads/)                           â”‚
â”‚  4. Pass file path to ML predictor                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
                           â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              Phase 1: ML Pipeline                            â”‚
â”‚                                                               â”‚
â”‚  predict_from_file(file_path)                              â”‚
â”‚  â”œâ”€ 1. preprocess_image() - Load + normalize                â”‚
â”‚  â”œâ”€ 2. Run ONNX inference - Get predictions                 â”‚
â”‚  â”œâ”€ 3. Apply temperature scaling - Calibrate confidence     â”‚
â”‚  â””â”€ 4. Return results dict with status_message (Urdu)      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
                           â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              FastAPI Backend (continued)                      â”‚
â”‚                                                               â”‚
â”‚  5. Save Prediction record to database                       â”‚
â”‚     INSERT INTO predictions (                               â”‚
â”‚       patient_id, image_path, class_index,                  â”‚
â”‚       confidence_score, inference_time_ms                   â”‚
â”‚     )                                                        â”‚
â”‚                                                               â”‚
â”‚  6. Create AuditLog entry (HIPAA compliance)                â”‚
â”‚     INSERT INTO audit_logs (                                â”‚
â”‚       endpoint_accessed,                                    â”‚
â”‚       action_details,                                       â”‚
â”‚       timestamp                                             â”‚
â”‚     )                                                        â”‚
â”‚                                                               â”‚
â”‚  7. Return PredictionResponse (JSON with English keys)      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
                           â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    Frontend (React)                          â”‚
â”‚                                                               â”‚
â”‚  Receive JSON response:                                     â”‚
â”‚  {                                                          â”‚
â”‚    "class_index": 1,                                       â”‚
â”‚    "confidence_score": 92.45,                             â”‚
â”‚    "inference_time_ms": 145,                              â”‚
â”‚    "status_message": "Ù†Ù…ÙˆÙ†ÛŒØ§ Ú©Ø§ Ø´Ø¨Û",  â† URDU             â”‚
â”‚    "patient_id": 1,                                       â”‚
â”‚    "prediction_id": 5                                     â”‚
â”‚  }                                                         â”‚
â”‚                                                             â”‚
â”‚  Display result to user                                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ðŸ§ª Test Script

Create `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Health check
print("1ï¸âƒ£  Health Check:")
response = requests.get(f"{BASE_URL}/health")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 2. Create patient
print("\n2ï¸âƒ£  Create Patient:")
patient_data = {
    "name": "Ø§Ø­Ù…Ø¯ Ø¹Ù„ÛŒ",
    "age": 45,
    "gender": "M",
    "contact_info": "03001234567"
}
response = requests.post(f"{BASE_URL}/api/v1/patients/", json=patient_data)
patient = response.json()
patient_id = patient["id"]
print(json.dumps(patient, indent=2, ensure_ascii=False))

# 3. List patients
print(f"\n3ï¸âƒ£  List Patients:")
response = requests.get(f"{BASE_URL}/api/v1/patients/")
print(f"Total patients: {len(response.json())}")

# 4. Get specific patient
print(f"\n4ï¸âƒ£  Get Patient {patient_id}:")
response = requests.get(f"{BASE_URL}/api/v1/patients/{patient_id}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False, default=str))

# 5. Make prediction (mock - using test image)
print(f"\n5ï¸âƒ£  Make Prediction:")
print("(Skipping in demo - requires actual DICOM file)")

# 6. Get audit logs
print(f"\n6ï¸âƒ£  Audit Logs:")
response = requests.get(f"{BASE_URL}/api/v1/audit-logs")
print(f"Total audit entries: {len(response.json())}")
for log in response.json()[:3]:
    print(f"  - {log['timestamp']}: {log['endpoint_accessed']}")

print("\nâœ… All tests completed!")
```

**Run it:**
```bash
python test_api.py
```

---

## ðŸ“Š Database State

After running the API:

### Patients Table
```
id | name      | age | gender | contact_info | created_at
1  | Ø§Ø­Ù…Ø¯ Ø¹Ù„ÛŒ   | 45  | M      | 03001234567  | 2026-03-11 10:30:00
2  | ÙØ§Ø·Ù…Û      | 38  | F      | 03009876543  | 2026-03-11 10:31:00
```

### Predictions Table
```
id | patient_id | image_path              | class_index | confidence_score | inference_time_ms | created_at
1  | 1          | uploads/xray_001.dcm    | 1           | 92.45            | 145               | 2026-03-11 10:35:00
2  | 1          | uploads/xray_002.dcm    | 0           | 87.12            | 142               | 2026-03-11 10:36:00
3  | 2          | uploads/xray_003.png    | 1           | 88.67            | 148               | 2026-03-11 10:37:00
```

### Audit Logs Table
```
id | endpoint_accessed                              | action_details                                  | timestamp
1  | /api/v1/predictions/predict-with-patient       | Ù…Ø±ÛŒØ¶ ID 1 Ú©Û’ Ù„ÛŒÛ’ X-ray Ú©Ø§ ØªØ¬Ø²ÛŒÛ...             | 2026-03-11 10:35:00
2  | /api/v1/predictions/predict-with-patient       | Ù†ØªÛŒØ¬Û: Ù†Ù…ÙˆÙ†ÛŒØ§ Ú©Ø§ Ø´Ø¨Û, Ø§Ø¹ØªÙ…Ø§Ø¯: 92.45%            | 2026-03-11 10:35:01
```

---

## ðŸ”Œ API Endpoints Reference

### Patient Management
```
POST   /api/v1/patients/                          Create patient
GET    /api/v1/patients/                          List patients (paginated)
GET    /api/v1/patients/{patient_id}              Get patient + predictions
PUT    /api/v1/patients/{patient_id}              Update patient
```

### Predictions
```
POST   /api/v1/predictions/predict-with-patient   â­ Main prediction endpoint
GET    /api/v1/predictions/{prediction_id}        Get prediction details
GET    /api/v1/patients/{patient_id}/predictions  Get all predictions for patient
```

### Audit & Health
```
GET    /api/v1/audit-logs                         List all audit logs
GET    /api/v1/audit-logs/patient/{patient_id}    Get audit for patient
GET    /health                                    Health check
```

---

## ðŸ” Key Security Features

âœ… **CORS Configured** - Middleware for cross-origin requests
âœ… **File Uploads** - Saved to disk, validated by ML predictor
âœ… **HIPAA Audit Logging** - Every action logged with timestamp
âœ… **Data Validation** - Pydantic schemas for request/response
âœ… **Database Relationships** - Foreign keys + cascade delete
âœ… **Error Handling** - Try/except with proper HTTP status codes
âœ… **JWT Ready** - Security layer for authentication (Phase 3)

---

## ðŸš¨ Common Issues & Fixes

### "Module not found: backend.app.main"
```bash
# Make sure you're in the project root
pwd  # Should end with /cv_project_2
pip install -e .  # Optional: install as editable package
```

### "No such table: patients"
```
Database tables are created automatically on first run.
If not, check:
1. DATABASE_URL is correct
2. SQLite database has write permissions
3. Try deleting *.db file if using SQLite
```

### "ML model not found"
```
First, generate the ONNX model:

from backend.app.ml.ml_pipeline import PneumoniaModel, export_to_onnx
model = PneumoniaModel()  # This downloads pre-trained EfficientNetB0
export_to_onnx(model)
```

### "Port 8000 already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or change port in .env
PORT=8001
```

---

## ðŸ“ˆ Next: Phase 3 (Frontend)

Phase 3 will use these APIs to build:
- React components for patient registration
- Drag-and-drop X-ray upload
- Real-time prediction display
- Urdu UI with i18next localization
- Audit log viewer for admins

---

## âœ¨ Summary: What You Have Now

```
âœ… ML Pipeline (Phase 1)
   â€¢ Model definition (EfficientNetB0)
   â€¢ ONNX export
   â€¢ Multi-format preprocessing (PNG/JPG/DICOM)
   â€¢ Temperature scaling for confidence

âœ… Backend (Phase 2)
   â€¢ 3 SQLAlchemy models (Patient, Prediction, AuditLog)
   â€¢ 10+ API endpoints (CRUD + predictions)
   â€¢ Pydantic validation
   â€¢ HIPAA audit logging
   â€¢ File upload handling
   â€¢ Full Urdu comments

âœ… Infrastructure
   â€¢ FastAPI app with CORS
   â€¢ SQLite/PostgreSQL support
   â€¢ Environment configuration
   â€¢ Error handling throughout

â³ Coming Next: Phase 3
   â€¢ React frontend
   â€¢ User authentication
   â€¢ Dashboard UI
   â€¢ Real-time notifications
```

---

**ðŸŽ‰ Ready to run Phase 1 + 2 together!**

```bash
uvicorn backend.app.main:app --reload
```

**Access at:** http://localhost:8000/docs

---

**Created:** March 11, 2026

