Layer	Example Tools
Frontend	Next.js / React + Tailwind + shadcn/ui
Backend API	FastAPI (Python) or Node.js (Express / NestJS)
Database	PostgreSQL + ChromaDB for embeddings
Authentication	Auth0 or Firebase Auth (role-based: recruiter vs admin)
Email/SMS	SendGrid / Twilio
Storage for voice recordings	AWS S3 (encrypted, HIPAA compliant bucket)
Deployment	Vercel (frontend) + AWS/GCP/Azure backend
---------
patients
Column	Type	Description
patient_id	UUID (PK)	Unique pseudonymized ID
first_name	TEXT (nullable / encrypted)	
last_name	TEXT (nullable / encrypted)	
date_of_birth	DATE (nullable / encrypted)	
gender	TEXT	
contact_email	TEXT (nullable / encrypted)	Stored separately with restricted access
phone_number	TEXT (nullable / encrypted)	
location	TEXT	City/State/Country
condition_summary	TEXT	Extracted from voice transcript
eligibility_status	ENUM(“eligible”, “maybe”, “ineligible”, “pending”)	Updated after matching
risk_score	FLOAT	ML-derived likelihood of eligibility
created_at	TIMESTAMP	
updated_at	TIMESTAMP	
---
trials
Column	Type	Description
trial_id	UUID (PK)	
nct_number	TEXT	ClinicalTrials.gov ID
title	TEXT	
phase	TEXT	e.g. “Phase II”
condition	TEXT	
location	TEXT	
inclusion_criteria	JSONB	Extracted structured form
exclusion_criteria	JSONB	
contact_email	TEXT	Sponsor/site contact
start_date	DATE	
end_date	DATE	
--
patient_trial_matches
Column	Type	Description
match_id	UUID (PK)	
patient_id	UUID (FK → patients)	
trial_id	UUID (FK → trials)	
match_score	FLOAT	Similarity score (0–1)
eligibility_status	ENUM(“eligible”, “pending”, “ineligible”)	
future_eligibility_date	DATE (nullable)	
last_contact_date	TIMESTAMP	
notes	TEXT	Recruiter comments