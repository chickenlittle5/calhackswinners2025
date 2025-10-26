1. Patient calls in. Initial Call or Follow-up Call where patient's data is fetched from the database.  
2. Patient decribes patients' condition and AI listens to fill out medical histroy.  Asks any follow up questions if needed.  Considers the location they would want to have their clinical trials at. Info stored or updated in patients
3. AI stores patient in recruiter database, allowing recruiters to follow up with patients as needed.
4. AI determines possible clinical trials currently, and also possible clinical trials in the future.  
5. AI Sends email to patient detailing their possible current clinical trials and future clinical trials they may be eligible for. Also providing contact information about studies or provide application link if applicable.  Also provides summary of of study's information.   Provides explanations of why  and recommendations on which ones they would reccomend based on patient's history.  Incoporate reccomendation score.  Allows patient freedom to sign up for the clinical trials themselves.  

**NLP / Data Extraction: A Hugging Face Transformer model for NER (Named Entity Recognition) to pull structured concepts like Condition, Current_Therapy, and Line_of_Treatment from the user's plain-English query

**The "Progression Map" (Mock): This is the key to the hackathon. You'd create a progression_rules.json file. It would look like this:
JSON
{
  "nsclc": {
    "1st-Line Therapy": "2nd-Line Therapy",
    "2nd-Line Therapy": "3rd-Line Therapy",
    "Stage 3": "Stage 4"
  },
  "breast_cancer": {
    "ER+": "ER_Refractory",
    "Local": "Metastatic"
  }
}
The AI agent would use this "map" to identify a "Next-Step Match": It sees the patient is On 2nd-Line Therapy and finds a trial that requires Failed 2nd-Line Therapy


For patient information, use  MIMIC-III Clinical Database
For possible clinical trials, ClinicalTrials.gov and extra I/E critera and load into ChromaDB

Voice Input → Speech-to-Text → NLP → Patient Vector (MIMIC-III) → Trial Vector (ChromaDB) → Similarity Match → Eligibility Check → Email Summary

Feature: Eliminate patient history after certain time has passed.?

Dashboard solves the problem of a busy site coordinator must call them back, manually read a long list of confusing pre-screening questions, and then schedule them

"Context: This tool would be an AI-powered agent that acts as a "Trial Radar." It would match a patient's current medical status to trials, but more importantly, it would map their next logical progression steps against the trial database.
"
***Predictive reccomendation is the key differentiator from curent market competititors.  Abilities to update database and remember past patients.  Also, Grove.ai is a premium, licensed product.

--------------------------------------
🧩 1. System Overview
You want a Recruiter Dashboard that enables clinical-trial recruiters to:
View patients who’ve interacted with the AI agent.
Filter by eligibility, interest, location, and trial phase.
See patient summaries (de-identified or pseudonymized).
Reach out manually (call/email/text).
Send follow-up reminders or scheduling emails.
Track recruitment funnel (screened → pre-screened → enrolled → retained).

--Hume.ai for best AI voice