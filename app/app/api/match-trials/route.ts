import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { condition, location, age, gender } = body;

    // Build query parameters for ClinicalTrials.gov API v2
    const params = new URLSearchParams();
    
    // Search by condition/disease
    if (condition) {
      params.append('query.cond', condition);
    }
    
    // Filter by location if provided
    if (location) {
      params.append('query.locn', location);
    }
    
    // Only recruiting studies
    params.append('filter.overallStatus', 'RECRUITING');
    
    // Page size
    params.append('pageSize', '20');
    
    // Format
    params.append('format', 'json');

    // Call ClinicalTrials.gov API v2
    const apiUrl = `https://clinicaltrials.gov/api/v2/studies?${params.toString()}`;
    
    console.log('Querying ClinicalTrials.gov:', apiUrl);
    
    const response = await fetch(apiUrl, {
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`ClinicalTrials.gov API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Extract NCT IDs from results
    const trials = data.studies || [];
    const nctIds: string[] = [];
    const trialDetails: Array<{
      nctId: string;
      title: string;
      condition: string;
      phase: string;
      location: string;
    }> = [];

    for (const study of trials) {
      const protocolSection = study.protocolSection || {};
      const identificationModule = protocolSection.identificationModule || {};
      const statusModule = protocolSection.statusModule || {};
      const designModule = protocolSection.designModule || {};
      const conditionsModule = protocolSection.conditionsModule || {};
      const contactsLocationsModule = protocolSection.contactsLocationsModule || {};
      
      const nctId = identificationModule.nctId || '';
      const title = identificationModule.officialTitle || identificationModule.briefTitle || '';
      const conditions = conditionsModule.conditions || [];
      const phases = designModule.phases || [];
      const locations = contactsLocationsModule.locations || [];
      
      // Check eligibility criteria
      const eligibilityModule = protocolSection.eligibilityModule || {};
      const minAge = eligibilityModule.minimumAge;
      const maxAge = eligibilityModule.maximumAge;
      const sex = eligibilityModule.sex; // ALL, FEMALE, MALE
      
      // Filter by age if available
      let ageEligible = true;
      if (age && (minAge || maxAge)) {
        // Simple age check (would need more sophisticated parsing in production)
        ageEligible = true; // Simplified for now
      }
      
      // Filter by gender if specified
      let genderEligible = true;
      if (gender && sex && sex !== 'ALL') {
        genderEligible = sex.toUpperCase() === gender.toUpperCase();
      }
      
      if (ageEligible && genderEligible && nctId) {
        nctIds.push(nctId);
        trialDetails.push({
          nctId,
          title: title.substring(0, 200), // Truncate long titles
          condition: conditions[0] || 'Not specified',
          phase: phases[0] || 'Not specified',
          location: locations[0]?.facility || 'Multiple locations'
        });
      }
    }

    console.log(`Found ${nctIds.length} eligible trials`);

    return NextResponse.json({
      success: true,
      nctIds,
      trialDetails,
      count: nctIds.length
    });

  } catch (error) {
    console.error('Error matching trials:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error',
        nctIds: [],
        trialDetails: []
      },
      { status: 500 }
    );
  }
}

