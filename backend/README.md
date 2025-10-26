# TrialSync Backend API

FastAPI backend for matching patients with clinical trials using ClinicalTrials.gov data.

## Features

- **ClinicalTrials.gov Integration**: Fetch and sync clinical trial data
- **Intelligent Matching**: Match patients with trials based on eligibility criteria
- **Supabase Integration**: Store and update eligibility data in real-time
- **RESTful API**: Clean API endpoints for frontend integration

## Setup

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /` - API information and available endpoints

### Matching Endpoints

#### Match Patient with Trials
```http
POST /match/patient/{patient_id}?min_score=50
```
Matches a specific patient with all available trials and updates the database.

**Response:**
```json
{
  "patient_id": "uuid",
  "patient_name": "John Doe",
  "current_eligible_count": 3,
  "future_eligible_count": 2,
  "current_eligible_trials": [...],
  "future_eligible_trials": [...]
}
```

#### Match Trial with Patients
```http
POST /match/trial/{trial_id}?min_score=50
```
Matches a specific trial with all available patients and updates the database.

#### Match All
```http
POST /match/all?min_score=50
```
Matches all patients with all trials. **Warning:** Can be computationally expensive.

### ClinicalTrials.gov Endpoints

#### Sync Trials
```http
POST /trials/sync
Content-Type: application/json

{
  "condition": "diabetes",
  "phase": ["PHASE3"],
  "max_results": 50
}
```
Fetches trials from ClinicalTrials.gov and adds them to the database.

#### Search Trials
```http
GET /trials/search?condition=diabetes&phase=PHASE3&page_size=20
```
Search ClinicalTrials.gov without syncing to database (preview only).

## Matching Algorithm

The matching engine evaluates patients against trials based on:

1. **Age Requirements** (30 points)
   - Checks if patient age falls within trial's min/max age range

2. **Gender Requirements** (40 points)
   - Matches patient gender with trial requirements

3. **Condition Matching** (20 points)
   - Compares patient conditions with trial conditions
   - Uses keyword matching and similarity analysis

4. **Location Proximity** (10 points)
   - Basic location matching

5. **Trial Status** (50 points)
   - Only actively recruiting trials are marked as "current eligible"

**Scoring:**
- 100 = Perfect match
- 70-99 = Good match
- 50-69 = Acceptable match
- <50 = Not a match (filtered out)

Patients are marked as:
- **Currently Eligible**: Score ≥50 AND meets all hard requirements
- **Future Eligible**: Score ≥50 BUT missing some criteria (e.g., age will qualify later, trial not yet recruiting)

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app and endpoints
│   ├── config.py                # Configuration settings
│   ├── database.py              # Supabase client
│   ├── clinicaltrials_client.py # ClinicalTrials.gov API
│   └── matching_engine.py       # Matching algorithm
├── requirements.txt
└── README.md
```

### Testing

```bash
# Run the server
uvicorn app.main:app --reload

# Test matching endpoint
curl -X POST http://localhost:8000/match/all

# Test sync endpoint
curl -X POST http://localhost:8000/trials/sync \
  -H "Content-Type: application/json" \
  -d '{"condition": "diabetes", "max_results": 10}'
```

## ClinicalTrials.gov API

This backend uses the [ClinicalTrials.gov API v2](https://clinicaltrials.gov/api/v2/), which provides:

- Trial metadata (title, phase, sponsor, etc.)
- Eligibility criteria (age, gender, conditions)
- Location information
- Recruitment status

**Rate Limits**: The API has rate limits. For production use, implement caching and request throttling.

## Future Enhancements

- [ ] NLP-based eligibility criteria parsing
- [ ] Vector embeddings for semantic condition matching
- [ ] Caching layer for API responses
- [ ] Background job scheduler for periodic syncing
- [ ] Patient notification system
- [ ] Advanced scoring with machine learning

