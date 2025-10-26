# Email Configuration Setup

This application uses Nodemailer to send clinical trial notification emails to patients.

## Required Environment Variables

Add these to your `.env.local` file:

```env
# Email Configuration (Nodemailer)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password-here
```

## Gmail Setup (Recommended for Testing)

1. **Go to Google Account Settings**

   - Visit: https://myaccount.google.com/

2. **Enable 2-Factor Authentication**

   - Security → 2-Step Verification
   - Follow the setup wizard

3. **Generate an App Password**

   - Security → 2-Step Verification → App passwords
   - Select "Mail" as the app
   - Select "Other" as the device and name it "TrialSync"
   - Click "Generate"
   - Copy the 16-character password (remove spaces)

4. **Update .env.local**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-actual-email@gmail.com
   SMTP_PASS=abc def hij klmn opqr  # <- Use this exact format or remove spaces
   ```

## Alternative Email Services

### Ethereal (Testing Only - Fake SMTP)

- Visit: https://ethereal.email/
- Click "Create Ethereal Account"
- Copy credentials:
  ```env
  SMTP_HOST=smtp.ethereal.email
  SMTP_PORT=587
  SMTP_USER=generated-username@ethereal.email
  SMTP_PASS=generated-password
  ```
- Emails won't actually send but you can view them at ethereal.email

### SendGrid SMTP

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-api-key
```

### AWS SES

```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASS=your-ses-smtp-password
```

## Testing

After setting up your SMTP credentials:

1. **Start the Next.js server:**

   ```bash
   npm run dev
   ```

2. **Add a test patient** via the dashboard with:

   - Your email address
   - A medical condition (e.g., "Diabetes")
   - Other required fields

3. **Check your email** for the trial notification!

## How It Works

1. **Patient is saved** (via dashboard or voice agent)
2. **Trials are matched** via ClinicalTrials.gov API
3. **Email is sent** with:
   - Full trial details for each NCT ID
   - Contact information (phone & email)
   - Study locations
   - Eligibility criteria
   - Links to ClinicalTrials.gov

## Email Preview

The email includes:

- 🔬 Professional header with gradient design
- 📋 Complete study summaries
- ✅ Eligibility criteria
- 📍 Study locations (up to 5 per trial)
- 📞 Contact information for study coordinators
- 🔗 Direct links to ClinicalTrials.gov

## Troubleshooting

### "Invalid login: 535 Authentication failed"

- Make sure 2FA is enabled on Gmail
- Use an App Password, not your regular password
- Remove spaces from the app password

### "Connection timeout"

- Check your SMTP_HOST and SMTP_PORT
- Try port 465 with `secure: true` in the code
- Check if your network/firewall blocks SMTP

### Emails not arriving

- Check spam folder
- Verify the SMTP_USER email is correct
- Try sending a test email from Gmail web to confirm the account works
- Check console logs for error messages

### For development/testing

Use Ethereal to avoid sending real emails during development
