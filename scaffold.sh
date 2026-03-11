#!/bin/bash

# Medical AI Application Repository Scaffold
# This script creates the complete directory structure for a production-grade full-stack application

echo "=========================================="
echo "Building Repository Structure..."
echo "=========================================="
echo ""

# Root level directories and files
echo "[1/7] Creating root-level configuration files..."
touch docker-compose.yml
touch docker-compose.dev.yml
touch README.md
touch README_UR.md
touch .env.example
touch .gitignore
touch quick-setup.sh
echo "âœ“ Root files created"
echo ""

# Backend structure
echo "[2/7] Creating backend directory structure..."
mkdir -p backend/app/core
mkdir -p backend/app/ml
mkdir -p backend/scripts
echo "âœ“ Backend directories created"
echo ""

# Backend app files
echo "[3/7] Creating backend application files..."
touch backend/app/__init__.py
touch backend/app/main.py
touch backend/app/models.py
touch backend/app/schemas.py
touch backend/app/api.py
touch backend/app/database.py
echo "âœ“ Backend app files created"
echo ""

# Backend core files
echo "[4/7] Creating backend core security and config files..."
touch backend/app/core/security.py
touch backend/app/core/config.py
echo "âœ“ Backend core files created"
echo ""

# Backend ML files
echo "[5/7] Creating backend ML pipeline files..."
touch backend/app/ml/__init__.py
touch backend/app/ml/ml_pipeline.py
touch backend/app/ml/pneumonia_model.onnx
echo "âœ“ Backend ML files created"
echo ""

# Backend scripts and requirements
echo "[6/7] Creating backend scripts and requirements..."
touch backend/scripts/init_db.py
touch backend/scripts/generate_mock_data.py
touch backend/requirements.txt
touch backend/Dockerfile
echo "âœ“ Backend scripts created"
echo ""

# Frontend structure
echo "[7/7] Creating frontend directory structure..."
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/pages
mkdir -p frontend/src/locales
mkdir -p frontend/src/api
echo "âœ“ Frontend directories created"
echo ""

# Frontend files
echo "[8/8] Creating frontend application files..."
touch frontend/src/App.tsx
touch frontend/src/main.tsx
touch frontend/src/index.css
touch frontend/src/locales/en.json
touch frontend/src/locales/ur.json
touch frontend/src/api/client.ts
touch frontend/package.json
touch frontend/Dockerfile
touch frontend/nginx.conf
echo "âœ“ Frontend files created"
echo ""

echo "=========================================="
echo "âœ“ Repository scaffold complete!"
echo "=========================================="
echo ""
echo "Project structure:"
echo ""
echo "medical-ai-app/"
echo "â”œâ”€â”€ docker-compose.yml"
echo "â”œâ”€â”€ docker-compose.dev.yml"
echo "â”œâ”€â”€ README.md"
echo "â”œâ”€â”€ README_UR.md"
echo "â”œâ”€â”€ .env.example"
echo "â”œâ”€â”€ .gitignore"
echo "â”œâ”€â”€ quick-setup.sh"
echo "â”œâ”€â”€ backend/"
echo "â”‚   â”œâ”€â”€ app/"
echo "â”‚   â”‚   â”œâ”€â”€ __init__.py"
echo "â”‚   â”‚   â”œâ”€â”€ main.py"
echo "â”‚   â”‚   â”œâ”€â”€ models.py"
echo "â”‚   â”‚   â”œâ”€â”€ schemas.py"
echo "â”‚   â”‚   â”œâ”€â”€ api.py"
echo "â”‚   â”‚   â”œâ”€â”€ database.py"
echo "â”‚   â”‚   â”œâ”€â”€ core/"
echo "â”‚   â”‚   â”‚   â”œâ”€â”€ security.py"
echo "â”‚   â”‚   â”‚   â””â”€â”€ config.py"
echo "â”‚   â”‚   â””â”€â”€ ml/"
echo "â”‚   â”‚       â”œâ”€â”€ __init__.py"
echo "â”‚   â”‚       â”œâ”€â”€ ml_pipeline.py"
echo "â”‚   â”‚       â””â”€â”€ pneumonia_model.onnx"
echo "â”‚   â”œâ”€â”€ scripts/"
echo "â”‚   â”‚   â”œâ”€â”€ init_db.py"
echo "â”‚   â”‚   â””â”€â”€ generate_mock_data.py"
echo "â”‚   â”œâ”€â”€ requirements.txt"
echo "â”‚   â””â”€â”€ Dockerfile"
echo "â””â”€â”€ frontend/"
echo "    â”œâ”€â”€ public/"
echo "    â”œâ”€â”€ src/"
echo "    â”‚   â”œâ”€â”€ App.tsx"
echo "    â”‚   â”œâ”€â”€ main.tsx"
echo "    â”‚   â”œâ”€â”€ index.css"
echo "    â”‚   â”œâ”€â”€ components/"
echo "    â”‚   â”œâ”€â”€ pages/"
echo "    â”‚   â”‚   â”œâ”€â”€ Dashboard.tsx"
echo "    â”‚   â”‚   â”œâ”€â”€ Predictions.tsx"
echo "    â”‚   â”‚   â””â”€â”€ Patients.tsx"
echo "    â”‚   â”œâ”€â”€ locales/"
echo "    â”‚   â”‚   â”œâ”€â”€ en.json"
echo "    â”‚   â”‚   â””â”€â”€ ur.json"
echo "    â”‚   â””â”€â”€ api/"
echo "    â”‚       â””â”€â”€ client.ts"
echo "    â”œâ”€â”€ package.json"
echo "    â”œâ”€â”€ Dockerfile"
echo "    â””â”€â”€ nginx.conf"
echo ""
echo "Ready to start development!"

