"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { Plus, Search, Download, Filter } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import type { Patient, Trial } from "@/types/database";

export default function DashboardPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [trials, setTrials] = useState<Trial[]>([]);
  const [loading, setLoading] = useState(true);
  const [patientSearch, setPatientSearch] = useState("");
  const [trialSearch, setTrialSearch] = useState("");
  const [isPatientDialogOpen, setIsPatientDialogOpen] = useState(false);
  const [isTrialDialogOpen, setIsTrialDialogOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [selectedTrial, setSelectedTrial] = useState<Trial | null>(null);
  const [isViewPatientOpen, setIsViewPatientOpen] = useState(false);
  const [isViewTrialOpen, setIsViewTrialOpen] = useState(false);
  const [isMatching, setIsMatching] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [matchingMessage, setMatchingMessage] = useState("");

  const supabase = createClient();
  const API_BASE_URL = "http://localhost:8000";

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

      // Fetch trials
      const { data: trialsData, error: trialsError } = await supabase
        .from('trials')
        .select('*')
        .order('created_at', { ascending: false });

      if (trialsError) {
        console.error('Error fetching trials:', trialsError);
      } else {
        setTrials(trialsData || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }

  // Sync trials from ClinicalTrials.gov
  async function syncTrials() {
    try {
      setIsSyncing(true);
      setMatchingMessage("Syncing trials from ClinicalTrials.gov...");

      const response = await fetch(`${API_BASE_URL}/trials/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          condition: null, // Sync all conditions
          phase: null,
          max_results: 50
        })
      });

      if (!response.ok) {
        throw new Error('Failed to sync trials');
      }

      const data = await response.json();
      setMatchingMessage(`Successfully synced ${data.synced_count} trials!`);
      
      // Refresh trials list
      await fetchData();
      
      setTimeout(() => setMatchingMessage(""), 3000);
    } catch (error) {
      console.error('Error syncing trials:', error);
      setMatchingMessage("Error syncing trials. Make sure the backend is running.");
      setTimeout(() => setMatchingMessage(""), 5000);
    } finally {
      setIsSyncing(false);
    }
  }

  // Match all patients with all trials
  async function matchAll() {
    try {
      setIsMatching(true);
      setMatchingMessage("Matching all patients with trials...");

      const response = await fetch(`${API_BASE_URL}/match/all`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to match patients');
      }

      const data = await response.json();
      setMatchingMessage(
        `Matched ${data.patients_processed} patients with ${data.trials_processed} trials. ` +
        `Found ${data.total_matches} eligible matches!`
      );
      
      // Refresh data to show updated eligibility
      await fetchData();
      
      setTimeout(() => setMatchingMessage(""), 5000);
    } catch (error) {
      console.error('Error matching:', error);
      setMatchingMessage("Error matching. Make sure the backend is running at http://localhost:8000");
      setTimeout(() => setMatchingMessage(""), 5000);
    } finally {
      setIsMatching(false);
    }
  }

  // Match a specific patient
  async function matchPatient(patientId: string) {
    try {
      setIsMatching(true);
      setMatchingMessage("Finding eligible trials for patient...");

      const response = await fetch(`${API_BASE_URL}/match/patient/${patientId}`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to match patient');
      }

      const data = await response.json();
      setMatchingMessage(
        `Found ${data.current_eligible_count} current and ${data.future_eligible_count} future eligible trials!`
      );
      
      // Refresh data
      await fetchData();
      
      setTimeout(() => setMatchingMessage(""), 4000);
    } catch (error) {
      console.error('Error matching patient:', error);
      setMatchingMessage("Error matching patient. Make sure the backend is running.");
      setTimeout(() => setMatchingMessage(""), 5000);
    } finally {
      setIsMatching(false);
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

  // Filter trials based on search
  const filteredTrials = trials.filter(trial => {
    const searchLower = trialSearch.toLowerCase();
    return (
      trial.trial_id.toLowerCase().includes(searchLower) ||
      trial.title.toLowerCase().includes(searchLower) ||
      (trial.condition && trial.condition.toLowerCase().includes(searchLower)) ||
      (trial.location && trial.location.toLowerCase().includes(searchLower))
    );
  });

  // Calculate stats
  const stats = {
    totalPatients: patients.length,
    activeTrials: trials.length,
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
      <header className="border-b bg-card sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
          <div className="fade-in">
            <h1 className="text-4xl glow-text mb-1">TrialSync</h1>
            <p className="text-muted-foreground text-sm mt-1 uppercase tracking-wider">
              Clinical Recruitment Platform
            </p>
          </div>
          <div className="flex items-center gap-3 fade-in delay-1">
            <Button 
              onClick={syncTrials} 
              disabled={isSyncing}
              className="bg-secondary text-secondary-foreground hover:bg-secondary/90 text-sm px-4 py-5"
            >
              {isSyncing ? "Syncing..." : "Sync Trials"}
            </Button>

            <Button 
              onClick={matchAll} 
              disabled={isMatching || patients.length === 0 || trials.length === 0}
              className="bg-accent text-accent-foreground hover:bg-accent/90 text-sm px-4 py-5"
            >
              {isMatching ? "Matching..." : "Match All"}
            </Button>

            <Dialog open={isPatientDialogOpen} onOpenChange={setIsPatientDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90 text-base px-6 py-5">
                  <Plus className="mr-2 h-5 w-5" /> Add Patient
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

            <Dialog open={isTrialDialogOpen} onOpenChange={setIsTrialDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90 text-base px-6 py-5">
                  <Plus className="mr-2 h-5 w-5" /> Add Trial
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card border-border max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader className="mb-6">
                  <DialogTitle className="text-2xl">Add New Clinical Trial</DialogTitle>
                  <DialogDescription className="text-base">
                    Enter trial information to add it to the system.
                  </DialogDescription>
                </DialogHeader>
                <TrialForm onSuccess={() => {
                  setIsTrialDialogOpen(false);
                  fetchData();
                }} />
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>

      {/* Status Message Banner */}
      {matchingMessage && (
        <div className="max-w-7xl mx-auto px-8 pt-6">
          <div className="bg-accent/20 border border-accent text-accent-foreground px-6 py-4 rounded-lg text-center text-base font-medium">
            {matchingMessage}
          </div>
        </div>
      )}

      {/* Stats Overview */}
      <section className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                Possible Trials
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{stats.activeTrials}</div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Main Content */}
      <section className="max-w-7xl mx-auto px-8 pb-16">
        <Tabs defaultValue="patients" className="slide-up delay-3">
          <TabsList className="bg-transparent border-b w-full justify-start rounded-none h-auto p-0">
            <TabsTrigger 
              value="patients" 
              className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-8 py-4 text-base"
            >
              PATIENTS
            </TabsTrigger>
            <TabsTrigger 
              value="trials"
              className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-8 py-4 text-base"
            >
              CLINICAL TRIALS
            </TabsTrigger>
          </TabsList>

          <TabsContent value="patients" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search patients by name, ID, condition..."
                  className="pl-10 w-[400px] bg-muted"
                  value={patientSearch}
                  onChange={(e) => setPatientSearch(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" /> Export CSV
                </Button>
                <Button variant="outline">
                  <Filter className="mr-2 h-4 w-4" /> Filter
                </Button>
              </div>
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
                          <div className="flex gap-2">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="text-sm"
                              onClick={() => {
                                setSelectedPatient(patient);
                                setIsViewPatientOpen(true);
                              }}
                            >
                              View
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="text-sm bg-accent/10 hover:bg-accent/20"
                              onClick={() => matchPatient(patient.patient_id)}
                              disabled={isMatching}
                            >
                              Match
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          <TabsContent value="trials" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search trials by name, phase, sponsor..."
                  className="pl-10 w-[400px] bg-muted"
                  value={trialSearch}
                  onChange={(e) => setTrialSearch(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" /> Export CSV
                </Button>
                <Button variant="outline">
                  <Filter className="mr-2 h-4 w-4" /> Filter
                </Button>
              </div>
            </div>

            <Card className="overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-card">
                    <TableHead className="text-sm font-semibold">Trial ID</TableHead>
                    <TableHead className="text-sm font-semibold">Study Name</TableHead>
                    <TableHead className="text-sm font-semibold">Phase</TableHead>
                    <TableHead className="text-sm font-semibold">Condition</TableHead>
                    <TableHead className="text-sm font-semibold">Location</TableHead>
                    <TableHead className="text-sm font-semibold">Start Date</TableHead>
                    <TableHead className="text-sm font-semibold">End Date</TableHead>
                    <TableHead className="text-sm font-semibold">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-base">Loading...</TableCell>
                    </TableRow>
                  ) : filteredTrials.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-base">No trials found</TableCell>
                    </TableRow>
                  ) : (
                    filteredTrials.map((trial) => (
                      <TableRow key={trial.trial_id} className="hover:bg-muted/50">
                        <TableCell className="font-mono text-sm">
                          {trial.trial_id.slice(0, 8)}...
                        </TableCell>
                        <TableCell className="font-medium text-base max-w-md">{trial.title}</TableCell>
                        <TableCell className="text-base">{trial.phase ? `Phase ${trial.phase}` : '-'}</TableCell>
                        <TableCell className="text-base">{trial.condition || '-'}</TableCell>
                        <TableCell className="text-base">{trial.location || '-'}</TableCell>
                        <TableCell className="text-base">
                          {trial.start_date ? new Date(trial.start_date).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell className="text-base">
                          {trial.end_date ? new Date(trial.end_date).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="text-sm"
                            onClick={() => {
                              setSelectedTrial(trial);
                              setIsViewTrialOpen(true);
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
          </TabsContent>
        </Tabs>
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

      {/* View Trial Dialog */}
      <Dialog open={isViewTrialOpen} onOpenChange={setIsViewTrialOpen}>
        <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader className="mb-4">
            <DialogTitle className="text-2xl">Trial Details</DialogTitle>
          </DialogHeader>
          {selectedTrial && (
            <div className="space-y-6">
              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">Trial Information</h3>
                <div>
                  <p className="text-sm text-muted-foreground">Trial ID</p>
                  <p className="font-mono text-sm">{selectedTrial.trial_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Study Name</p>
                  <p className="font-medium text-lg">{selectedTrial.title}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Phase</p>
                    <p>{selectedTrial.phase ? `Phase ${selectedTrial.phase}` : '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Condition</p>
                    <p>{selectedTrial.condition || '-'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">Location & Timeline</h3>
                <div>
                  <p className="text-sm text-muted-foreground">Location</p>
                  <p>{selectedTrial.location || '-'}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Start Date</p>
                    <p>{selectedTrial.start_date ? new Date(selectedTrial.start_date).toLocaleDateString() : '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">End Date</p>
                    <p>{selectedTrial.end_date ? new Date(selectedTrial.end_date).toLocaleDateString() : '-'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold border-b border-border pb-2">System Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Created</p>
                    <p className="text-sm">{new Date(selectedTrial.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Updated</p>
                    <p className="text-sm">{new Date(selectedTrial.updated_at).toLocaleString()}</p>
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
    diagnosed_conditions: [] as string[],
    current_medications: [] as string[]
  });

  const supabase = createClient();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const submitData = {
      ...formData,
      age: formData.age ? parseInt(formData.age) : null
    };
    
    const { error } = await supabase
      .from('patients')
      .insert([submitData] as any);

    if (error) {
      console.error('Error adding patient:', error);
      alert('Error adding patient');
    } else {
      alert('Patient added successfully!');
      onSuccess();
    }
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
            value={formData.diagnosed_conditions.join(', ')}
            onChange={(e) => setFormData({
              ...formData, 
              diagnosed_conditions: e.target.value.split(',').map(s => s.trim()).filter(s => s)
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
            value={formData.current_medications.join(', ')}
            onChange={(e) => setFormData({
              ...formData, 
              current_medications: e.target.value.split(',').map(s => s.trim()).filter(s => s)
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

// Trial Form Component
function TrialForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    title: '',
    phase: '',
    condition: '',
    location: '',
    start_date: '',
    end_date: ''
  });

  const supabase = createClient();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const { error } = await supabase
      .from('trials')
      .insert([formData] as any);

    if (error) {
      console.error('Error adding trial:', error);
      alert('Error adding trial');
    } else {
      alert('Clinical trial added successfully!');
      onSuccess();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">Trial Information</h3>
        
        <div>
          <Label htmlFor="title" className="text-base">Study Name *</Label>
          <Input
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            required
            placeholder="e.g., A Phase III Study of Novel Treatment for NSCLC"
            className="mt-2 h-11"
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <Label htmlFor="phase" className="text-base">Phase</Label>
            <Select value={formData.phase} onValueChange={(value) => setFormData({...formData, phase: value})}>
              <SelectTrigger className="mt-2 h-11">
                <SelectValue placeholder="Select phase" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="I">Phase I</SelectItem>
                <SelectItem value="II">Phase II</SelectItem>
                <SelectItem value="III">Phase III</SelectItem>
                <SelectItem value="IV">Phase IV</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="condition" className="text-base">Condition/Disease *</Label>
            <Input
              id="condition"
              value={formData.condition}
              onChange={(e) => setFormData({...formData, condition: e.target.value})}
              required
              placeholder="e.g., Non-Small Cell Lung Cancer"
              className="mt-2 h-11"
            />
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">Location & Timeline</h3>
        
        <div>
          <Label htmlFor="location" className="text-base">Location *</Label>
          <Input
            id="location"
            value={formData.location}
            onChange={(e) => setFormData({...formData, location: e.target.value})}
            required
            placeholder="e.g., Stanford Medical Center, CA"
            className="mt-2 h-11"
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <Label htmlFor="start_date" className="text-base">Start Date</Label>
            <Input
              id="start_date"
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({...formData, start_date: e.target.value})}
              className="mt-2 h-11"
            />
          </div>
          <div>
            <Label htmlFor="end_date" className="text-base">End Date</Label>
            <Input
              id="end_date"
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({...formData, end_date: e.target.value})}
              className="mt-2 h-11"
            />
          </div>
        </div>
      </div>

      <Button type="submit" className="w-full bg-primary text-primary-foreground h-12 text-base mt-6">
        Add Clinical Trial
      </Button>
    </form>
  );
}