export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      patients: {
        Row: {
          patient_id: string
          first_name: string | null
          last_name: string | null
          date_of_birth: string | null
          age: number | null
          gender: string | null
          contact_email: string | null
          phone_number: string | null
          location: string | null
          condition_summary: string | null
          diagnosed_conditions: Json | null
          current_medications: Json | null
          current_eligible_trials: Json | null
          future_eligible_trials: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          patient_id?: string
          first_name?: string | null
          last_name?: string | null
          date_of_birth?: string | null
          age?: number | null
          gender?: string | null
          contact_email?: string | null
          phone_number?: string | null
          location?: string | null
          condition_summary?: string | null
          diagnosed_conditions?: Json | null
          current_medications?: Json | null
          current_eligible_trials?: Json | null
          future_eligible_trials?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          patient_id?: string
          first_name?: string | null
          last_name?: string | null
          date_of_birth?: string | null
          age?: number | null
          gender?: string | null
          contact_email?: string | null
          phone_number?: string | null
          location?: string | null
          condition_summary?: string | null
          diagnosed_conditions?: Json | null
          current_medications?: Json | null
          current_eligible_trials?: Json | null
          future_eligible_trials?: Json | null
          created_at?: string
          updated_at?: string
        }
      }
      trials: {
        Row: {
          trial_id: string
          title: string
          phase: string | null
          condition: string | null
          location: string | null
          start_date: string | null
          end_date: string | null
          eligible_patients: Json | null
          future_eligible_patients: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          trial_id?: string
          title: string
          phase?: string | null
          condition?: string | null
          location?: string | null
          start_date?: string | null
          end_date?: string | null
          eligible_patients?: Json | null
          future_eligible_patients?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          trial_id?: string
          title?: string
          phase?: string | null
          condition?: string | null
          location?: string | null
          start_date?: string | null
          end_date?: string | null
          eligible_patients?: Json | null
          future_eligible_patients?: Json | null
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}

export type Patient = Database['public']['Tables']['patients']['Row']
export type Trial = Database['public']['Tables']['trials']['Row']
