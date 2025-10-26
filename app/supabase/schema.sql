-- Supabase Schema for Clinical Trial Recruitment Platform
-- Based on architecture.md specification

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create patients table
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    age INTEGER,
    gender TEXT,
    contact_email TEXT,
    phone_number TEXT,
    location TEXT,
    condition_summary TEXT,
    diagnosed_conditions JSONB,
    current_medications JSONB,
    current_eligible_trials JSONB,
    future_eligible_trials JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create trials table
CREATE TABLE trials (
    trial_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    phase TEXT,
    condition TEXT,
    location TEXT,
    start_date DATE,
    end_date DATE,
    eligible_patients JSONB DEFAULT '[]'::jsonb,
    future_eligible_patients JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_patients_condition ON patients(condition_summary);
CREATE INDEX idx_trials_condition ON trials(condition);
CREATE INDEX idx_trials_phase ON trials(phase);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trials_updated_at BEFORE UPDATE ON trials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE trials ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth requirements)
-- For now, allowing all operations for development
CREATE POLICY "Allow all operations on patients" ON patients
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on trials" ON trials
    FOR ALL USING (true);
