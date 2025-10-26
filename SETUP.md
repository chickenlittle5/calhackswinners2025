# TrialSync - Setup Guide

Complete guide to set up and run the Clinical Trial Recruitment Platform.

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│   Next.js UI    │◄────────│  FastAPI Backend │◄────────│ ClinicalTrials.gov  │
│  (Port 3000)    │         │   (Port 8000)    │         │       API v2        │
└────────┬────────┘         └─────────┬────────┘         └─────────────────────┘
         │                            │
         │                            │
         └───────────┬────────────────┘
                     │
              ┌──────▼──────┐
              │  Supabase   │
              │  PostgreSQL │
              └─────────────┘
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Supabase Account** (free tier works)
- **Git**

## Part 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login
3. Create a new project
4. Save your **Project URL** and **anon/public key**

### 1.2 Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Open the file: `app/supabase/schema.sql`
3. Copy and paste the entire contents into the SQL Editor
4. Click **Run**

This creates two tables:
- `patients` - Patient demographic and medical data
- `trials` - Clinical trial information

## Part 2: Backend Setup (FastAPI)

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Create Virtual Environment

```bash
python3 -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

**Get these values from:**
- Supabase Dashboard → Settings → API

### 2.5 Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

**Test it:**
```bash
curl http://localhost:8000
```

You should see API information.

## Part 3: Frontend Setup (Next.js)

### 3.1 Navigate to App Directory

Open a **new terminal** and:

```bash
cd app
```

### 3.2 Install Dependencies

```bash
npm install
```

### 3.3 Configure Environment Variables

Create a `.env.local` file in the `app` directory:

```bash
# app/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### 3.4 Start Frontend Server

```bash
npm run dev
```

The UI will be available at: **http://localhost:3000**

## Part 4: Using the System

### 4.1 Add Patient Data

1. Go to http://localhost:3000
2. Click **"Add Patient"**
3. Fill in the form:
   - First Name, Last Name
   - Date of Birth, Age
   - Gender
   - Contact Email, Phone
   - Location
   - Condition Summary
   - Diagnosed Conditions (comma-separated)
   - Current Medications (comma-separated)
4. Click **"Add Patient"**

### 4.2 Sync Trials from ClinicalTrials.gov

**Option 1: Sync All Recruiting Trials**
1. Click **"Sync Trials"** in the header
2. Wait for the process to complete
3. Trials will appear in the "Clinical Trials" tab

**Option 2: Use Backend API Directly**
```bash
curl -X POST http://localhost:8000/trials/sync \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "diabetes",
    "phase": ["PHASE3"],
    "max_results": 50
  }'
```

### 4.3 Match Patients with Trials

**Option 1: Match All**
- Click **"Match All"** button in the header
- This matches all patients with all trials

**Option 2: Match Individual Patient**
- Go to "Patients" tab
- Find a patient
- Click **"Match"** button next to their name

**Option 3: Use API**
```bash
# Match specific patient
curl -X POST http://localhost:8000/match/patient/{patient_id}

# Match all
curl -X POST http://localhost:8000/match/all
```

### 4.4 View Eligibility Results

After matching, view results:

1. **In Patient View:**
   - Click "View" on any patient
   - Scroll to "Eligible Trials" section
   - See "Current Eligible" and "Future Eligible" lists

2. **In Trial View:**
   - Click "View" on any trial
   - See list of eligible patients

3. **In Database:**
   - Supabase Dashboard → Table Editor
   - Check `current_eligible_trials` and `future_eligible_trials` columns (JSONB)

## How the Matching Works

The matching algorithm evaluates each patient-trial pair based on:

### 1. **Age Requirements** (30 points)
- Patient age must fall within trial's `min_age` and `max_age`
- Hard requirement: Fails if outside range

### 2. **Gender** (40 points)
- Must match trial's `gender` requirement
- Hard requirement if trial specifies gender

### 3. **Condition Match** (20 points)
- Compares `condition_summary` and `diagnosed_conditions` with trial's `condition`
- Uses keyword matching and similarity

### 4. **Location** (10 points)
- Soft preference for same location

### 5. **Trial Status** (50 points)
- Must be "RECRUITING" or "NOT_YET_RECRUITING"

**Scoring:**
- 100 = Perfect match
- 70-99 = Good match
- 50-69 = Acceptable match
- <50 = Not eligible

**Categories:**
- **Currently Eligible**: Meets ALL requirements + score ≥50
- **Future Eligible**: Score ≥50 but missing some criteria (e.g., trial not yet open, age will qualify later)

## API Endpoints Reference

### Backend API (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/match/patient/{id}` | POST | Match one patient |
| `/match/trial/{id}` | POST | Match one trial |
| `/match/all` | POST | Match all patients & trials |
| `/trials/sync` | POST | Sync from ClinicalTrials.gov |
| `/trials/search` | GET | Search ClinicalTrials.gov (preview) |

### Frontend (Port 3000)

- **Dashboard**: http://localhost:3000
- Patients tab, Trials tab
- Add Patient/Trial forms
- View detailed information
- Sync and Match buttons

## Troubleshooting

### Backend not connecting to Supabase
- Check `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
- Verify keys in Supabase Dashboard → Settings → API

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check `API_BASE_URL` in `app/app/page.tsx` is `http://localhost:8000`
- Check CORS settings in `backend/app/main.py`

### No trials syncing
- ClinicalTrials.gov API may have rate limits
- Try syncing fewer trials (`max_results: 10`)
- Check backend console for errors

### Matching not working
- Ensure both patients AND trials exist in database
- Check backend logs for detailed error messages
- Verify Supabase connection

### Next.js not loading styles
- Hard refresh browser: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)
- Clear browser cache
- Restart Next.js dev server

## Project Structure

```
calhackswinners2025/
├── app/                          # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── layout.tsx           # App layout
│   │   └── globals.css          # Global styles (neon theme)
│   ├── components/ui/           # shadcn/ui components
│   ├── lib/supabase/           # Supabase client
│   ├── types/database.ts       # TypeScript types
│   ├── supabase/schema.sql     # Database schema
│   └── package.json
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── main.py             # API endpoints
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Supabase operations
│   │   ├── clinicaltrials_client.py  # ClinicalTrials.gov API
│   │   └── matching_engine.py  # Matching algorithm
│   ├── requirements.txt
│   └── README.md
│
├── architecture.md              # System architecture
├── workflow.md                 # End-to-end workflow
└── SETUP.md                    # This file
```

## Next Steps

1. **Add More Patients**: Test with diverse patient profiles
2. **Sync Condition-Specific Trials**: Use condition filters when syncing
3. **Review Matches**: Check eligibility results and matching scores
4. **Refine Matching**: Adjust `min_score` parameter for stricter/looser matching
5. **Export Data**: Use "Export CSV" buttons (coming soon)
6. **Notifications**: Implement email notifications for matches (future enhancement)

## Production Deployment

### Backend (FastAPI)
- Deploy to: Railway, Render, or AWS Lambda
- Use production WSGI server (Gunicorn + Uvicorn)
- Add authentication middleware
- Implement rate limiting

### Frontend (Next.js)
- Deploy to: Vercel (recommended), Netlify, or AWS
- Configure environment variables in platform
- Enable production optimizations

### Database (Supabase)
- Already hosted in production
- Enable RLS (Row Level Security) for production
- Set up proper authentication

## Support

For issues or questions:
1. Check Supabase logs
2. Check backend console output
3. Check browser console (F12)
4. Review API responses with `curl -v`

---

**Built with:**
- Next.js 15 + React 19
- FastAPI + Python 3.9+
- Supabase (PostgreSQL)
- ClinicalTrials.gov API v2
- Tailwind CSS + shadcn/ui

