# TrialSync

## Inspiration

Finding the right clinical trial is often confusing and time-consuming for patients. Many individuals miss opportunities to access potentially life-changing treatments because of barriers like complicated eligibility criteria, lack of awareness, or overwhelming amounts of medical information. At the same time, researchers and recruiters struggle to reach suitable candidates efficiently. TrialSync aims to kill these two birds with one stone.

## What it does

TrialSync is an AI-driven platform that intelligently connects patients with clinical trials they are eligible for — both current and future opportunities. It consists of an integrated pipeline that bridges patients, recruiters, and clinical trial data sources through automation and intelligent decision-making:

* **Patient Interaction:** Patients describe their medical conditions naturally through conversation. The AI listens, extracts relevant medical history, and asks follow-up questions to ensure accuracy and completeness. It also considers the patient’s preferences, such as desired clinical trial location or study type.
* **Data Management:** All information is securely stored or updated in the patients database. This data is then synchronized with a recruiter-facing database, allowing recruiters to view, monitor, and follow up with interested patients.
* **Trial Matching:** The AI fetches trial information from ClinicalTrials.gov and other sources, then filters and ranks potential matches based on the patient’s medical profile, location, and eligibility criteria.
* **Intelligent Recommendations:** TrialSync assigns a recommendation score to each trial, reflecting how well it aligns with the patient’s condition, treatment goals, and preferences. It also generates clear explanations for its recommendations to promote transparency.
* **Automated Communication:** The system automatically emails patients a detailed summary of their matched trials — including study details, contact information, links to apply, and a concise explanation of why the AI recommends each trial. Patients can independently decide which studies they wish to pursue.

## How we built it

### Frontend

* Next.js / React
* Tailwind CSS
* shadcn/ui

### Backend

* LiveKit
* Voice Agent
* Python
* Twilio
* Supabase
* Claude API

## Challenges we ran into

It took us a while to determine our idea due to all the tracks that were offered; I had a difficult time choosing! Once we did figure out thought, we became incredibly efficient in our work. When we began working on it, we also had trouble setting up the dependencies we would need, since it was our first time working with them.

## Accomplishments that we're proud of

We created a full-stack web application that incorporated a Voice AI capable of naturally conversing with patients to gather and update their medical history. The system intelligently matched patients to relevant clinical trials, generated personalized recommendations with reasoning, and automatically sent detailed email summaries of their potential matches.

## What we learned

As all have us don't have too much cumulative experience with hackathons, we learned a lot that we could apply to future ones we choose to attend:

1. **Definitely plan ahead** — We didn't look at the tracks until the day of, so we had to do a lot of research the first thing we got here. Looking back, it would've been a great idea to look into some of the sponsors and their products beforehand.
2. **Pick an idea and stick with it** — In our brainstorm phase, we spent a lot of time bouncing back between a few good ideas we had. Had we just stuck with one, we would've ended up saving a lot of time.
3. **Don't count Wifi coming back on.**

## What's next for TrialSync

Our next steps focus on making TrialSync more powerful, transparent, and patient-centered:

* **HIPAA Compliance & Data Security:** Implement advanced encryption, anonymization, and audit trails to meet healthcare privacy standards and ensure safe handling of sensitive patient data.
* **Expanded Voice Intelligence:** Improve the Voice AI’s medical reasoning and conversational ability, enabling it to detect nuanced health details, clarify uncertainties, and provide empathetic interactions.
