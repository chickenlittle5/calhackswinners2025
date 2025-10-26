// Quick test script to verify SMTP configuration
// Run with: node test-email.js

const nodemailer = require('nodemailer');
require('dotenv').config({ path: '.env.local' });

async function testEmail() {
  console.log('📧 Testing email configuration...\n');
  
  console.log('SMTP Configuration:');
  console.log('  Host:', process.env.SMTP_HOST);
  console.log('  Port:', process.env.SMTP_PORT);
  console.log('  User:', process.env.SMTP_USER);
  console.log('  Pass:', process.env.SMTP_PASS ? '✅ Configured' : '❌ Missing');
  console.log('');

  try {
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT),
      secure: false,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });

    console.log('🔄 Verifying connection...');
    await transporter.verify();
    console.log('✅ SMTP connection verified!\n');

    console.log('📨 Sending test email...');
    const info = await transporter.sendMail({
      from: `"TrialSync Test" <${process.env.SMTP_USER}>`,
      to: process.env.SMTP_USER, // Send to yourself
      subject: '✅ TrialSync Email Test - Success!',
      html: `
        <div style="font-family: Arial, sans-serif; padding: 20px;">
          <h1 style="color: #00ff9f;">✅ Email Working!</h1>
          <p>Your SMTP configuration is working correctly.</p>
          <p><strong>Configuration:</strong></p>
          <ul>
            <li>Host: ${process.env.SMTP_HOST}</li>
            <li>Port: ${process.env.SMTP_PORT}</li>
            <li>User: ${process.env.SMTP_USER}</li>
          </ul>
          <p>You can now receive clinical trial notifications!</p>
        </div>
      `,
    });

    console.log('✅ Test email sent successfully!');
    console.log('   Message ID:', info.messageId);
    console.log('\n📬 Check your inbox:', process.env.SMTP_USER);
    console.log('   (Don\'t forget to check spam folder!)');

  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error('\n💡 Common fixes:');
    console.error('   1. Remove spaces from SMTP_PASS in .env.local');
    console.error('   2. Make sure 2FA is enabled on Gmail');
    console.error('   3. Use an App Password (not regular password)');
    console.error('   4. Check if "Less secure app access" is disabled (should be)');
  }
}

testEmail();

