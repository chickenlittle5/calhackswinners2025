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
first_name	TEXT (nullable / encrypted)	Stored separately with restricted access
last_name	TEXT (nullable / encrypted)	Stored separately with restricted access
date_of_birth	DATE (nullable / encrypted)	Stored separately with restricted access
gender	TEXT	
contact_email	TEXT (nullable / encrypted)	Stored separately with restricted access
phone_number	TEXT (nullable / encrypted)	Stored separately with restricted access
location	TEXT	City/State/Country
condition_summary	TEXT	Extracted from voice transcript
current_eligibile_trials
future_eligibile_trials	JSONB	Example: [{"trial_id": "...", "expected_date": "YYYY-MM-DD"}]
created_at	TIMESTAMP	
updated_at	TIMESTAMP	
--
trials
Column	Type	Notes
trial_id	UUID	NCT ID
title	TEXT	Trial title
phase	TEXT	Trial phase
condition	TEXT	Condition focus
location	TEXT	
start_date / end_date	DATE	
eligible_patients	JSONB or array of patient_ids	Only store IDs of patients eligible for this 
future_eligible_patients 