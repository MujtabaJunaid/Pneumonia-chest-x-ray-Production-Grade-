# ðŸ³ DOCKER QUICK START GUIDE

**Pneumonia AI Detector - One-Click Deployment**

---

## âš¡ QUICKEST START (30 seconds)

### Windows/Mac/Linux

```bash
# 1. Navigate to project root
cd c:\Users\hp\cv_project_2

# 2. Run one command
chmod +x quick-setup.sh
./quick-setup.sh
```

That's it! The script will:
- âœ… Build Docker images
- âœ… Start 3 containers (PostgreSQL, Backend, Frontend)
- âœ… Create database tables
- âœ… Generate 1,000 patients + 2,500 predictions
- âœ… Display access URLs

**Time**: ~2-3 minutes

---

## ðŸŒ ACCESS AFTER SETUP

Once complete, open your browser:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost |
| **API Docs** | http://localhost/api/docs |
| **API Base** | http://localhost/api/v1 |
| **Health** | http://localhost/health |

---

## ðŸ“Š WHAT GETS CREATED

```
Database:
â”œâ”€ 1,000 Patient records (Pakistani names + phones)
â”œâ”€ 2,500 Prediction records (clinical data)
â””â”€ Audit logs (automated)

Services:
â”œâ”€ Frontend (React on port 80)
â”œâ”€ Backend (FastAPI on port 8000)
â””â”€ Database (PostgreSQL port 5432)
```

---

## ðŸ”‘ DATABASE CREDENTIALS

```
Host: db (or localhost)
Port: 5432
Username: pneumonia_user
Password: pneumonia_secure_password_2026
Database: pneumonia_detector
```

---

## ðŸ§ª TEST THE SYSTEM

### Via Web UI

1. Open http://localhost
2. Enter Patient ID: `1`
3. Upload a medical image (PNG/JPG/DICOM)
4. Click "Analyze Image"
5. View results

### Via API

```bash
# Get patient
curl http://localhost/api/v1/patients/1

# List predictions
curl http://localhost/api/v1/patients/1/predictions

# API documentation
open http://localhost/api/docs
```

---

## ðŸ› ï¸ USEFUL COMMANDS

### Logs
```bash
docker-compose logs -f           # All services
docker-compose logs -f backend   # Backend only
```

### Database
```bash
# Access PostgreSQL CLI
docker-compose exec db psql -U pneumonia_user -d pneumonia_detector

# Count patients
docker-compose exec db psql -U pneumonia_user -d pneumonia_detector -c "SELECT COUNT(*) FROM patient;"

# View first 5 patients
docker-compose exec db psql -U pneumonia_user -d pneumonia_detector -c "SELECT * FROM patient LIMIT 5;"
```

### Container Management
```bash
docker-compose ps              # Show running containers
docker-compose restart         # Restart all
docker-compose down            # Stop everything
docker-compose up -d           # Start in background
```

---

## ðŸ› TROUBLESHOOTING

### Can't connect to http://localhost
- Check if containers are running: `docker-compose ps`
- Check Docker is running on your system
- Wait 30 seconds (containers need time to start)
- Check logs: `docker-compose logs frontend`

### Backend returns 502 error
- Check backend health: `docker-compose exec backend curl http://localhost:8000/health`
- Check database connection: `docker-compose logs backend`
- Restart backend: `docker-compose restart backend`

### Mock data didn't generate
- Check script ran: `docker-compose logs backend`
- Generate manually: `docker-compose exec backend python scripts/generate_mock_data.py`
- Verify Faker installed: `docker-compose exec backend pip list | grep Faker`

### Database errors
- Check PostgreSQL is running: `docker-compose ps db`
- Check connection: `docker-compose exec db pg_isready -U pneumonia_user`
- View logs: `docker-compose logs db`

---

## ðŸ“¦ FILES INCLUDED IN PHASE 4

```
âœ… backend/Dockerfile                  - FastAPI container
âœ… frontend/Dockerfile                 - React + Nginx container
âœ… frontend/nginx.conf                 - Nginx reverse proxy config
âœ… docker-compose.yml                  - Container orchestration
âœ… backend/scripts/generate_mock_data.py - Mock data generator
âœ… quick-setup.sh                      - One-command setup
âœ… PHASE_4_COMPLETE.md                 - Detailed documentation
âœ… DOCKER_QUICK_START.md              - This file
```

---

## ðŸ” SECURITY NOTES

**Development Setup** (as provided):
- Default PostgreSQL password used
- Debug mode disabled
- CORS enabled for localhost

**Production Changes Needed**:
- [ ] Change PostgreSQL password
- [ ] Enable SSL/HTTPS
- [ ] Configure CORS for production domain
- [ ] Enable authentication
- [ ] Set up backups
- [ ] Enable monitoring

---

## ðŸ“š FULL DOCUMENTATION

For detailed information:
- See [PHASE_4_COMPLETE.md](PHASE_4_COMPLETE.md) - Complete Phase 4 guide
- See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Full project overview
- See [PHASE_3_COMPLETE.md](PHASE_3_COMPLETE.md) - Frontend documentation
- See [DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md) - All phases summary

---

## â“ FAQ

**Q: How do I stop the containers?**
A: `docker-compose down`

**Q: Can I reuse the same database?**
A: Yes, data persists in Docker volumes.

**Q: How do I remove all data and start fresh?**
A: `docker-compose down -v` (removes volumes)

**Q: Can I run this on a server?**
A: Yes! Works on any system with Docker.

**Q: What if I need to update code?**
A: Rebuild: `docker-compose up -d --build`

---

## ðŸš€ NEXT STEPS

1. **Prepare your X-ray model**
   - Export EfficientNetB0 to ONNX format
   - Place at `backend/app/ml/pneumonia_model.onnx`

2. **Deploy**
   ```bash
   ./quick-setup.sh
   ```

3. **Test the system**
   - Upload sample X-rays
   - Check predictions

4. **Scale to production**
   - Change database password
   - Enable HTTPS
   - Deploy to server

---

## ðŸ’¡ TIPS

- **For better performance**: Allocate more CPU/RAM in Docker Desktop settings
- **For development**: Keep `--reload` flag in backend Dockerfile
- **For production**: Remove `--reload` and set `DEBUG=false`
- **For data backup**: Run `docker-compose exec db pg_dump ... > backup.sql`

---

**Status**: âœ… READY TO DEPLOY

**Next**: Run `./quick-setup.sh`

---

Need help? Check the detailed documentation in [PHASE_4_COMPLETE.md](PHASE_4_COMPLETE.md)

