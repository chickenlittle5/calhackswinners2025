# TrialSync - Quick Start

## 🚀 Start Everything in 3 Steps

### Step 1: Setup Database (One-time)

1. Go to [supabase.com](https://supabase.com) and create a project
2. Copy your Project URL and anon key
3. In Supabase SQL Editor, run: `app/supabase/schema.sql`

### Step 2: Start Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your Supabase credentials
echo "SUPABASE_URL=your_url_here" > .env
echo "SUPABASE_KEY=your_key_here" >> .env

# Start server
uvicorn app.main:app --reload
```

Backend runs on: **http://localhost:8000**

### Step 3: Start Frontend

```bash
# In a new terminal
cd app

# If first time
npm install

# Create .env.local with your Supabase credentials
echo "NEXT_PUBLIC_SUPABASE_URL=your_url_here" > .env.local
echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key_here" >> .env.local

# Start server
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 🎯 Usage

1. **Add Patients**: Click "Add Patient" button
2. **Sync Trials**: Click "Sync Trials" button (fetches from ClinicalTrials.gov)
3. **Match**: Click "Match All" or "Match" next to individual patients
4. **View Results**: Click "View" on any patient to see eligible trials

---

## 🔧 Quick Commands

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend
cd app && npm run dev

# Test Backend
curl http://localhost:8000

# Match All via API
curl -X POST http://localhost:8000/match/all

# Sync Trials for Diabetes
curl -X POST http://localhost:8000/trials/sync \
  -H "Content-Type: application/json" \
  -d '{"condition": "diabetes", "max_results": 20}'
```

---

## 📁 Important Files

- **Database Schema**: `app/supabase/schema.sql`
- **Backend API**: `backend/app/main.py`
- **Frontend Dashboard**: `app/app/page.tsx`
- **Matching Logic**: `backend/app/matching_engine.py`
- **Full Setup Guide**: `SETUP.md`

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check `.env` file exists with correct credentials |
| Frontend can't connect | Ensure backend is running on port 8000 |
| No trials syncing | Check ClinicalTrials.gov API (may have rate limits) |
| Styles not loading | Hard refresh browser: Cmd+Shift+R or Ctrl+Shift+R |

---

**Need more help?** See `SETUP.md` for detailed documentation.

