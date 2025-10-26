"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { Patient } from "@/types/database";

export default function DashboardPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [patientSearch, setPatientSearch] = useState("");
  const [isPatientDialogOpen, setIsPatientDialogOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [isViewPatientOpen, setIsViewPatientOpen] = useState(false);

  const supabase = createClient();

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      setLoading(true);
      
      // Fetch patients
      const { data: patientsData, error: patientsError } = await supabase
        .from('patients')
        .select('*')
        .order('created_at', { ascending: false });

      if (patientsError) {
        console.error('Error fetching patients:', patientsError);
      } else {
        setPatients(patientsData || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }

  // Filter patients based on search
  const filteredPatients = patients.filter(patient => {
    const searchLower = patientSearch.toLowerCase();
    return (
      patient.patient_id.toLowerCase().includes(searchLower) ||
      (patient.first_name && patient.first_name.toLowerCase().includes(searchLower)) ||
      (patient.last_name && patient.last_name.toLowerCase().includes(searchLower)) ||
      (patient.condition_summary && patient.condition_summary.toLowerCase().includes(searchLower))
    );
  });

  // Calculate stats
  const stats = {
    totalPatients: patients.length,
    matchedPatients: patients.filter(p => 
      p.current_eligible_trials && 
      Array.isArray(p.current_eligible_trials) && 
      p.current_eligible_trials.length > 0
    ).length,
    totalTrialsFound: patients.reduce((sum, p) => {
      if (p.current_eligible_trials && Array.isArray(p.current_eligible_trials)) {
        return sum + p.current_eligible_trials.length;
      }
      return sum;
    }, 0)
  };

  const getStatusBadgeClass = (status: string) => {
    const statusClasses: { [key: string]: string } = {
      'active': 'status-active',
      'eligible': 'status-eligible',
      'recruiting': 'status-recruiting',
      'pending': 'status-pending',
      'maybe': 'status-maybe',
      'completed': 'status-completed',
      'ineligible': 'status-ineligible',
      'declined': 'status-declined'
    };
    return statusClasses[status] || '';
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-50 backdrop-blur-sm" style={{ backgroundColor: 'hsl(var(--card))' }}>
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="fade-in">
            <h1 className="text-4xl glow-text mb-1">TrialSync</h1>
            <p className="text-muted-foreground text-sm mt-1 uppercase tracking-wider">
              Clinical Recruitment Platform
            </p>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      <section className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="stat-card relative overflow-hidden slide-up delay-2">
            <CardHeader className="pb-3">
              <CardDescription className="text-sm uppercase tracking-wider font-semibold">
                Total Patients
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{stats.totalPatients}</div>
            </CardContent>
          </Card>

          <Card className="stat-card relative overflow-hidden slide-up delay-3">
            <CardHeader className="pb-3">
              <CardDescription className="text-sm uppercase tracking-wider font-semibold">
                Matched Patients
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{stats.matchedPatients}</div>
              {stats.totalPatients > 0 && (
                <p className="text-sm text-muted-foreground mt-2">
                  {Math.round((stats.matchedPatients / stats.totalPatients) * 100)}% of patients
                </p>
              )}
            </CardContent>
          </Card>

          <Card className="stat-card relative overflow-hidden slide-up delay-4">
            <CardHeader className="pb-3">
              <CardDescription className="text-sm uppercase tracking-wider font-semibold">
                Eligible Trials
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{stats.totalTrialsFound}</div>
              {stats.matchedPatients > 0 && (
                <p className="text-sm text-muted-foreground mt-2">
                  {(stats.totalTrialsFound / stats.matchedPatients).toFixed(1)} avg per patient
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Main Content */}
      <section className="max-w-7xl mx-auto px-8 pb-16">
        <div className="slide-up delay-3">
          <div className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <Input
                type="search"
                placeholder="Search patients by name, ID, condition..."
                className="w-[300px]"
                value={patientSearch}
                onChange={(e) => setPatientSearch(e.target.value)}
              />
              
              <Dialog open={isPatientDialogOpen} onOpenChange={setIsPatientDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-5">
                    <Plus className="mr-2 h-4 w-4" /> Add Patient
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-card border-border max-w-4xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader className="mb-6">
                    <DialogTitle className="text-2xl">Add New Patient</DialogTitle>
                    <DialogDescription className="text-base">
                      Enter patient information to add them to the system.
                    </DialogDescription>
                  </DialogHeader>
                  <PatientForm onSuccess={() => {
                    setIsPatientDialogOpen(false);
                    fetchData();
                  }} />
                </DialogContent>
              </Dialog>
            </div>

            <Card className="overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-card">
                    <TableHead className="text-sm font-semibold">Patient ID</TableHead>
                    <TableHead className="text-sm font-semibold">Name</TableHead>
                    <TableHead className="text-sm font-semibold">Age</TableHead>
                    <TableHead className="text-sm font-semibold">Gender</TableHead>
                    <TableHead className="text-sm font-semibold">Location</TableHead>
                    <TableHead className="text-sm font-semibold">Condition</TableHead>
                    <TableHead className="text-sm font-semibold">Enrolled Date</TableHead>
                    <TableHead className="text-sm font-semibold">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-base">Loading...</TableCell>
                    </TableRow>
                  ) : filteredPatients.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-base">No patients found</TableCell>
                    </TableRow>
                  ) : (
                    filteredPatients.map((patient) => (
                      <TableRow key={patient.patient_id} className="hover:bg-muted/50">
                        <TableCell className="font-mono text-sm">
                          {patient.patient_id.slice(0, 8)}...
                        </TableCell>
                        <TableCell className="font-medium text-base">
                          {patient.first_name} {patient.last_name}
                        </TableCell>
                        <TableCell className="text-base">
                          {patient.age ?? '-'}
                        </TableCell>
                        <TableCell className="text-base">{patient.gender || '-'}</TableCell>
                        <TableCell className="text-base">{patient.location || '-'}</TableCell>
                        <TableCell className="text-base">{patient.condition_summary || '-'}</TableCell>
                        <TableCell className="text-base">
                          {new Date(patient.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="text-xs"
                            onClick={() => {
                              setSelectedPatient(patient);
                              setIsViewPatientOpen(true);
                            }}
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </div>
        </div>
      </section>

      {/* View Patient Dialog */}
      <Dialog open={isViewPatientOpen} onOpenChange={setIsViewPatientOpen}>
        <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader className="mb-4">
            <DialogTitle className="text-2xl">Patient Details</DialogTitle>
          </DialogHeader>
          {selectedPatient && (
            <div className="space-y-6">
              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">Personal Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Patient ID</p>
                    <p className="font-mono text-sm">{selectedPatient.patient_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-medium">{selectedPatient.first_name} {selectedPatient.last_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Date of Birth</p>
                    <p>{selectedPatient.date_of_birth ? new Date(selectedPatient.date_of_birth).toLocaleDateString() : '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Age</p>
                    <p>{selectedPatient.age ?? '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Gender</p>
                    <p>{selectedPatient.gender || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Location</p>
                    <p>{selectedPatient.location || '-'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">Contact Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p>{selectedPatient.contact_email || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Phone</p>
                    <p>{selectedPatient.phone_number || '-'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">Medical Information</h3>
                <div>
                  <p className="text-sm text-muted-foreground">Primary Condition</p>
                  <p>{selectedPatient.condition_summary || '-'}</p>
                </div>
                {selectedPatient.diagnosed_conditions && Array.isArray(selectedPatient.diagnosed_conditions) && selectedPatient.diagnosed_conditions.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Diagnosed Conditions</p>
                    <div className="flex flex-wrap gap-2">
                      {(selectedPatient.diagnosed_conditions as string[]).map((condition, i) => (
                        <Badge key={i} variant="secondary">{condition}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {selectedPatient.current_medications && Array.isArray(selectedPatient.current_medications) && selectedPatient.current_medications.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Current Medications</p>
                    <div className="flex flex-wrap gap-2">
                      {(selectedPatient.current_medications as string[]).map((med, i) => (
                        <Badge key={i} variant="secondary">{med}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Eligible Clinical Trials Section */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">Eligible Clinical Trials</h3>
                {selectedPatient.current_eligible_trials && Array.isArray(selectedPatient.current_eligible_trials) && selectedPatient.current_eligible_trials.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground mb-3">
                      Found {selectedPatient.current_eligible_trials.length} matching trial{selectedPatient.current_eligible_trials.length > 1 ? 's' : ''}
                    </p>
                    <div className="space-y-3">
                      {(selectedPatient.current_eligible_trials as string[]).map((nctId, i) => (
                        <div key={i} className="bg-muted/50 border border-border rounded-lg p-4 hover:border-primary/50 transition-colors">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-primary font-mono font-bold text-sm">{nctId}</span>
                                <Badge variant="secondary" className="text-xs">Recruiting</Badge>
                              </div>
                              <p className="text-xs text-muted-foreground">
                                Click the link below to view full trial details on ClinicalTrials.gov
          </p>
        </div>
          <a
                              href={`https://clinicaltrials.gov/study/${nctId}`}
            target="_blank"
            rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-md text-sm font-medium transition-colors whitespace-nowrap"
                            >
                              View Details
                              <svg 
                                className="w-4 h-4" 
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
          </a>
        </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="bg-muted/30 border border-dashed border-border rounded-lg p-6 text-center">
                    <p className="text-muted-foreground">No eligible trials found yet</p>
                    <p className="text-xs text-muted-foreground mt-1">Trials will appear here after matching</p>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">System Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Created</p>
                    <p className="text-sm">{new Date(selectedPatient.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Updated</p>
                    <p className="text-sm">{new Date(selectedPatient.updated_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

    </div>
  );
}

// Patient Form Component
function PatientForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    age: '',
    gender: '',
    contact_email: '',
    phone_number: '',
    location: '',
    condition_summary: '',
    diagnosed_conditions: '',
    current_medications: ''
  });

  const supabase = createClient();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const submitData = {
      ...formData,
      age: formData.age ? parseInt(formData.age) : null,
      diagnosed_conditions: formData.diagnosed_conditions 
        ? formData.diagnosed_conditions.split(',').map(s => s.trim()).filter(s => s)
        : [],
      current_medications: formData.current_medications
        ? formData.current_medications.split(',').map(s => s.trim()).filter(s => s)
        : []
    };
    
    // Insert patient and get the ID back
    const { data: insertedPatient, error } = await supabase
      .from('patients')
      .insert([submitData] as any)
      .select()
      .single();

    if (error || !insertedPatient) {
      console.error('Error adding patient:', error);
      alert('Error adding patient');
      return;
    }

    // Match trials using ClinicalTrials.gov API
    try {
      const matchResponse = await fetch('/api/match-trials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          condition: formData.condition_summary,
          location: formData.location,
          age: formData.age ? parseInt(formData.age) : null,
          gender: formData.gender
        }),
      });

      const matchData = await matchResponse.json();

      if (matchData.success && matchData.nctIds.length > 0) {
        // Update patient with matched trial NCT IDs
        const updateResult: any = await (supabase as any)
          .from('patients')
          .update({ 
            current_eligible_trials: matchData.nctIds 
          })
          .eq('patient_id', (insertedPatient as any).patient_id);

        if (updateResult.error) {
          console.error('Error updating patient with trials:', updateResult.error);
        } else {
          console.log(`✅ Found ${matchData.nctIds.length} eligible trials for patient`);
          
          // Send email with trial details
          if (formData.contact_email) {
            try {
              console.log('📧 Sending trial notification email...');
              const emailResponse = await fetch('/api/send-trial-email', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  patientEmail: formData.contact_email,
                  patientName: formData.first_name || 'Patient',
                  nctIds: matchData.nctIds
                }),
              });

              const emailData = await emailResponse.json();
              
              if (emailData.success) {
                console.log(`✅ Email sent successfully with ${emailData.trialsFound} trial details`);
              } else {
                console.warn('⚠️ Email sending failed:', emailData.error);
              }
            } catch (emailError) {
              console.error('Error sending email:', emailError);
              // Don't fail if email fails
            }
          }
        }
      }
    } catch (matchError) {
      console.error('Error matching trials:', matchError);
      // Don't fail the patient creation if trial matching fails
    }

    alert('Patient added successfully! Finding eligible trials and sending notification email...');
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">Personal Information</h3>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <Label htmlFor="first_name" className="text-base">First Name *</Label>
            <Input
              id="first_name"
              value={formData.first_name}
              onChange={(e) => setFormData({...formData, first_name: e.target.value})}
              required
              className="mt-2 h-11"
            />
          </div>
          <div>
            <Label htmlFor="last_name" className="text-base">Last Name *</Label>
            <Input
              id="last_name"
              value={formData.last_name}
              onChange={(e) => setFormData({...formData, last_name: e.target.value})}
              required
              className="mt-2 h-11"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <Label htmlFor="date_of_birth" className="text-base">Date of Birth</Label>
            <Input
              id="date_of_birth"
              type="date"
              value={formData.date_of_birth}
              onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
              className="mt-2 h-11"
            />
          </div>
          <div>
            <Label htmlFor="age" className="text-base">Age</Label>
            <Input
              id="age"
              type="number"
              value={formData.age}
              onChange={(e) => setFormData({...formData, age: e.target.value})}
              placeholder="e.g., 45"
              className="mt-2 h-11"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="gender" className="text-base">Gender</Label>
          <Select value={formData.gender} onValueChange={(value) => setFormData({...formData, gender: value})}>
            <SelectTrigger className="mt-2 h-11">
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">Contact Information</h3>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <Label htmlFor="contact_email" className="text-base">Email</Label>
            <Input
              id="contact_email"
              type="email"
              value={formData.contact_email}
              onChange={(e) => setFormData({...formData, contact_email: e.target.value})}
              className="mt-2 h-11"
            />
          </div>
          <div>
            <Label htmlFor="phone_number" className="text-base">Phone Number</Label>
            <Input
              id="phone_number"
              value={formData.phone_number}
              onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
              className="mt-2 h-11"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="location" className="text-base">Location</Label>
          <Input
            id="location"
            value={formData.location}
            onChange={(e) => setFormData({...formData, location: e.target.value})}
            placeholder="City, State, Country"
            className="mt-2 h-11"
          />
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">Medical Information</h3>
        
        <div>
          <Label htmlFor="condition_summary" className="text-base">Primary Condition *</Label>
          <Input
            id="condition_summary"
            value={formData.condition_summary}
            onChange={(e) => setFormData({...formData, condition_summary: e.target.value})}
            required
            placeholder="e.g., Non-Small Cell Lung Cancer, Stage 3"
            className="mt-2 h-11"
          />
        </div>

        <div>
          <Label htmlFor="diagnosed_conditions" className="text-base">Diagnosed Conditions</Label>
          <textarea
            id="diagnosed_conditions"
            value={formData.diagnosed_conditions}
            onChange={(e) => setFormData({
              ...formData, 
              diagnosed_conditions: e.target.value
            })}
            placeholder="e.g., NSCLC, Hypertension, Diabetes Type 2 (comma-separated)"
            className="mt-2 w-full min-h-[80px] rounded-md border border-input bg-muted px-3 py-2 text-sm text-foreground resize-y"
          />
          <p className="text-xs text-muted-foreground mt-1">Enter multiple conditions separated by commas</p>
        </div>

        <div>
          <Label htmlFor="current_medications" className="text-base">Current Medications</Label>
          <textarea
            id="current_medications"
            value={formData.current_medications}
            onChange={(e) => setFormData({
              ...formData, 
              current_medications: e.target.value
            })}
            placeholder="e.g., Pembrolizumab, Lisinopril, Metformin (comma-separated)"
            className="mt-2 w-full min-h-[80px] rounded-md border border-input bg-muted px-3 py-2 text-sm text-foreground resize-y"
          />
          <p className="text-xs text-muted-foreground mt-1">Enter multiple medications separated by commas</p>
        </div>
    </div>

      <Button type="submit" className="w-full bg-primary text-primary-foreground h-12 text-base mt-6">
        Add Patient
      </Button>
    </form>
  );
}