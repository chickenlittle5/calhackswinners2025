import { NextResponse } from 'next/server';
import nodemailer from 'nodemailer';

interface TrialDetail {
  nctId: string;
  title: string;
  briefSummary: string;
  phase: string;
  condition: string;
  eligibilityCriteria: string;
  minAge: string;
  maxAge: string;
  gender: string;
  contacts: Array<{
    name: string;
    role: string;
    phone: string;
    email: string;
  }>;
  locations: Array<{
    facility: string;
    city: string;
    state: string;
    country: string;
  }>;
  trialUrl: string;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { patientEmail, patientName, nctIds } = body;

    // Validate required fields
    if (!patientEmail || !patientName || !nctIds || !Array.isArray(nctIds) || nctIds.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields: patientEmail, patientName, nctIds' },
        { status: 400 }
      );
    }

    console.log(`📧 Preparing to send trial email to ${patientEmail} for ${nctIds.length} trials`);

    // Step 1: Fetch detailed information for each trial from ClinicalTrials.gov
    const trialDetails: TrialDetail[] = [];

    for (const nctId of nctIds) {
      try {
        const apiUrl = `https://clinicaltrials.gov/api/v2/studies/${nctId}`;
        console.log(`🔍 Fetching details for ${nctId}...`);
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          console.warn(`Failed to fetch ${nctId}: ${response.status}`);
          continue;
        }

        const data = await response.json();
        const study = data.protocolSection || {};
        
        const identification = study.identificationModule || {};
        const description = study.descriptionModule || {};
        const design = study.designModule || {};
        const conditions = study.conditionsModule || {};
        const eligibility = study.eligibilityModule || {};
        const contacts = study.contactsLocationsModule || {};

        // Extract contact information
        const centralContacts = (contacts.centralContacts || []).map((contact: any) => ({
          name: contact.name || 'Not specified',
          role: contact.role || '',
          phone: contact.phone || '',
          email: contact.email || '',
        }));

        // Extract locations
        const locationsList = (contacts.locations || []).slice(0, 5).map((loc: any) => ({
          facility: loc.facility || '',
          city: loc.city || '',
          state: loc.state || '',
          country: loc.country || '',
        }));

        trialDetails.push({
          nctId,
          title: identification.officialTitle || identification.briefTitle || '',
          briefSummary: description.briefSummary || 'No summary available',
          phase: design.phases?.join(', ') || 'Not specified',
          condition: conditions.conditions?.join(', ') || 'Not specified',
          eligibilityCriteria: eligibility.eligibilityCriteria || 'Not specified',
          minAge: eligibility.minimumAge || 'Not specified',
          maxAge: eligibility.maximumAge || 'Not specified',
          gender: eligibility.sex || 'All',
          contacts: centralContacts,
          locations: locationsList,
          trialUrl: `https://clinicaltrials.gov/study/${nctId}`,
        });

        console.log(`✅ Fetched details for ${nctId}`);
      } catch (error) {
        console.error(`Error fetching trial ${nctId}:`, error);
        // Continue with other trials
      }
    }

    if (trialDetails.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Could not fetch details for any trials' },
        { status: 500 }
      );
    }

    // Step 2: Generate HTML email
    const emailHtml = generateTrialEmailHtml(patientName, trialDetails);

    // Step 3: Send email via Nodemailer
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: false, // true for 465, false for other ports
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });

    const mailOptions = {
      from: `"TrialSync" <${process.env.SMTP_USER}>`,
      to: patientEmail,
      subject: `Your Personalized Clinical Trial Recommendations (${trialDetails.length} Trials)`,
      html: emailHtml,
    };

    const info = await transporter.sendMail(mailOptions);

    console.log(`✅ Email sent successfully to ${patientEmail}. Message ID: ${info.messageId}`);

    return NextResponse.json({
      success: true,
      trialsFound: trialDetails.length,
      messageId: info.messageId,
      trials: trialDetails.map(t => ({
        nctId: t.nctId,
        title: t.title,
      })),
    });

  } catch (error) {
    console.error('Error sending trial email:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

function generateTrialEmailHtml(patientName: string, trials: TrialDetail[]): string {
  let html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    .container {
      background: white;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .header {
      background: linear-gradient(135deg, #00ff9f, #00d4ff);
      color: #0a0e17;
      padding: 40px 30px;
      text-align: center;
    }
    .header h1 {
      margin: 0 0 10px 0;
      font-size: 32px;
      font-weight: bold;
    }
    .content {
      padding: 30px;
    }
    .trial-card {
      background: #f9f9f9;
      border-left: 4px solid #00ff9f;
      padding: 25px;
      margin: 25px 0;
      border-radius: 5px;
    }
    .trial-title {
      color: #0a0e17;
      font-size: 22px;
      font-weight: bold;
      margin-bottom: 15px;
      line-height: 1.3;
    }
    .trial-detail {
      margin: 12px 0;
      font-size: 15px;
    }
    .trial-detail strong {
      color: #00d4ff;
      font-weight: 600;
      display: inline-block;
      min-width: 140px;
    }
    .section-heading {
      color: #00d4ff;
      font-size: 18px;
      font-weight: 600;
      margin: 20px 0 10px 0;
      border-bottom: 2px solid #00ff9f;
      padding-bottom: 5px;
    }
    .contact-box {
      background: white;
      padding: 15px;
      margin: 10px 0;
      border-radius: 5px;
      border: 1px solid #e0e0e0;
    }
    .contact-box strong {
      color: #0a0e17;
      font-size: 16px;
    }
    .location-item {
      background: white;
      padding: 10px;
      margin: 5px 0;
      border-radius: 5px;
      font-size: 14px;
    }
    .cta-button {
      display: inline-block;
      background: #00ff9f;
      color: #0a0e17;
      padding: 14px 28px;
      text-decoration: none;
      border-radius: 5px;
      font-weight: bold;
      margin-top: 15px;
      font-size: 16px;
    }
    .footer {
      margin-top: 30px;
      padding: 25px 30px;
      background: #f5f5f5;
      text-align: center;
      color: #666;
      font-size: 14px;
      line-height: 1.8;
    }
    .footer strong {
      color: #333;
    }
    .eligibility-box {
      background: #e8f9f4;
      padding: 15px;
      border-radius: 5px;
      margin: 15px 0;
      font-size: 14px;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🔬 Your Clinical Trial Matches</h1>
      <p style="margin: 0; font-size: 18px;">Personalized recommendations based on your medical profile</p>
    </div>
    
    <div class="content">
      <p style="font-size: 18px;">Hello <strong>${patientName}</strong>,</p>
      
      <p style="font-size: 16px;">Thank you for your interest in clinical trials! Based on your medical history and condition, we've identified <strong>${trials.length}</strong> clinical trial${trials.length > 1 ? 's' : ''} that may be suitable for you.</p>
      
      <p style="font-size: 16px;">Below you'll find detailed information about each trial, including how to apply and who to contact.</p>
`;

  // Add trial cards
  trials.forEach((trial, index) => {
    html += `
      <div class="trial-card">
        <div class="trial-title">
          ${index + 1}. ${trial.title}
        </div>
        
        <div class="trial-detail">
          <strong>NCT ID:</strong> ${trial.nctId}
        </div>
        
        <div class="trial-detail">
          <strong>Phase:</strong> ${trial.phase}
        </div>
        
        <div class="trial-detail">
          <strong>Condition:</strong> ${trial.condition}
        </div>
        
        <div class="section-heading">📋 Study Summary</div>
        <p style="margin: 10px 0; font-size: 15px; line-height: 1.6;">
          ${trial.briefSummary.substring(0, 500)}${trial.briefSummary.length > 500 ? '...' : ''}
        </p>
        
        <div class="section-heading">✅ Eligibility Criteria</div>
        <div class="eligibility-box">
          <strong>Age Range:</strong> ${trial.minAge} - ${trial.maxAge}<br>
          <strong>Gender:</strong> ${trial.gender}<br><br>
          <div style="font-size: 13px; max-height: 150px; overflow-y: auto;">
            ${trial.eligibilityCriteria.substring(0, 600)}${trial.eligibilityCriteria.length > 600 ? '...' : ''}
          </div>
        </div>
`;

    // Add locations
    if (trial.locations.length > 0) {
      html += `
        <div class="section-heading">📍 Study Locations</div>
`;
      trial.locations.forEach(location => {
        if (location.facility || location.city) {
          html += `
        <div class="location-item">
          <strong>${location.facility || 'Location'}</strong><br>
          ${location.city}${location.state ? `, ${location.state}` : ''}${location.country ? `, ${location.country}` : ''}
        </div>
`;
        }
      });
    }

    // Add contacts
    if (trial.contacts.length > 0 && trial.contacts[0].name !== 'Not specified') {
      html += `
        <div class="section-heading">📞 How to Apply - Contact Information</div>
`;
      trial.contacts.forEach(contact => {
        html += `
        <div class="contact-box">
          <strong>${contact.name}</strong>${contact.role ? ` - ${contact.role}` : ''}<br>
`;
        if (contact.phone) {
          html += `          📱 Phone: <a href="tel:${contact.phone}">${contact.phone}</a><br>\n`;
        }
        if (contact.email) {
          html += `          ✉️ Email: <a href="mailto:${contact.email}">${contact.email}</a><br>\n`;
        }
        html += `        </div>\n`;
      });
    }

    html += `
        <a href="${trial.trialUrl}" class="cta-button">View Full Details on ClinicalTrials.gov →</a>
      </div>
`;
  });

  html += `
    </div>
    
    <div class="footer">
      <p><strong>📝 Next Steps:</strong></p>
      <p>Review the trials above and reach out directly to the study coordinators using the contact information provided. They will guide you through the screening and enrollment process.</p>
      
      <p><strong>⚠️ Important:</strong> This information is for educational purposes only. Please consult with your healthcare provider before making any decisions about participating in a clinical trial.</p>
      
      <p>If you have any questions or need assistance, please don't hesitate to reach out.</p>
      
      <p style="margin-top: 20px;">Best regards,<br><strong>TrialSync Team</strong></p>
    </div>
  </div>
</body>
</html>
`;

  return html;
}

