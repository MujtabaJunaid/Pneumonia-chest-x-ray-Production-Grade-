# ðŸš€ QUICK START GUIDE - Frontend Setup

## Prerequisites
- Node.js 16+ and npm installed
- Backend running on `http://localhost:8000`

## Step 1: Install Dependencies
```bash
cd frontend
npm install
```

## Step 2: Start Development Server
```bash
npm run dev
```

Expected output:
```
âžœ  frontend
âžœ  Local:   http://localhost:5173
âžœ  press h to show help
```

## Step 3: Open in Browser
Visit: **http://localhost:5173**

## Step 4: Test the Application

1. **Check Backend Status**
   - Look for the health indicator in the navbar
   - Should show âœ… Connected (green pulsing dot)

2. **Select Language** (Optional)
   - Click "English" or "Ø§Ø±Ø¯Ùˆ" to toggle language
   - UI will switch between LTR and RTL layouts

3. **Analyze X-ray**
   - Enter Patient ID (e.g., 1)
   - Upload PNG/JPG/DICOM file (drag & drop supported)
   - Click "Analyze Image"
   - Results appear with:
     - Color-coded diagnosis (green=normal, red=pneumonia)
     - Confidence score (as percentage)
     - Inference time (in ms)
     - Urdu status message

## Available Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code (if configured)
npm run lint
```

## Backend Integration

The frontend communicates with the backend at:
- **Base URL**: http://localhost:8000
- **Prediction Endpoint**: POST /api/v1/predictions/predict-with-patient
- **Health Check**: GET /health

## Troubleshooting

### "Cannot reach backend"
- âŒ Backend not running â†’ Start backend first: `uvicorn backend.app.main:app --reload`
- âŒ Wrong port â†’ Check backend is on port 8000

### "File upload fails"
- âŒ Wrong file format â†’ Use PNG, JPG, or DICOM only
- âŒ File too large â†’ Max file size is typically 50MB

### "Results not showing"
- âŒ Patient ID invalid â†’ Verify patient exists in database
- âŒ API error â†’ Check backend logs for detailed error

### "Language toggle not working"
- âŒ Refresh the page
- âŒ Check browser console for errors (F12)

## Environment Variables

To use a custom backend URL, create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

Then update `src/api/client.ts` to use `import.meta.env.VITE_API_URL`.

## Performance Tips

1. **For slower connections**: Reduce timeout in `api/client.ts` or increase it
2. **For large files**: Consider adding upload progress indicator
3. **For frequently accessed data**: Add caching to Axios interceptors

## Next Steps

1. âœ… Install dependencies (`npm install`)
2. âœ… Start frontend dev server (`npm run dev`)
3. âœ… Test file upload and analysis
4. âœ… Toggle between English/Urdu
5. âœ… Check audit logs in backend

## File Structure

```
frontend/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â””â”€â”€ client.ts           # Axios API client
â”‚   â”œâ”€â”€ pages/
â”‚   â”‚   â”œâ”€â”€ Dashboard.tsx       # Main analysis page
â”‚   â”‚   â”œâ”€â”€ Predictions.tsx     # Predictions history
â”‚   â”‚   â””â”€â”€ Patients.tsx        # Patient management
â”‚   â”œâ”€â”€ locales/
â”‚   â”‚   â”œâ”€â”€ en.json             # English translations
â”‚   â”‚   â””â”€â”€ ur.json             # Urdu translations
â”‚   â”œâ”€â”€ i18n.ts                 # i18next configuration
â”‚   â”œâ”€â”€ App.tsx                 # Main app component
â”‚   â”œâ”€â”€ main.tsx                # Vite entry point
â”‚   â””â”€â”€ index.css               # Global styles
â”œâ”€â”€ package.json                # Dependencies
â”œâ”€â”€ vite.config.ts              # Vite configuration
â”œâ”€â”€ tsconfig.json               # TypeScript configuration
â”œâ”€â”€ tailwind.config.js          # TailwindCSS configuration
â””â”€â”€ postcss.config.js           # PostCSS configuration
```

## Health Check

The app automatically checks backend health every 30 seconds. You'll see:
- ðŸŸ¢ Green dot = Backend running
- ðŸ”´ Red dot = Backend offline

## Language Support

**Supported Languages:**
- ðŸ‡¬ðŸ‡§ English (LTR)
- ðŸ‡µðŸ‡° Ø§Ø±Ø¯Ùˆ (RTL)

Click the language button in the navbar to switch.

