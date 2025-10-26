# TrialSync - Clinical Trial Recruitment Platform

A modern Next.js application for managing clinical trial recruitment, built with TypeScript, Tailwind CSS, shadcn/ui, and Supabase.

## Features

- 📊 **Dashboard Overview**: Real-time stats for patients and trials
- 👥 **Patient Management**: Add, search, and manage patient records
- 🔬 **Trial Management**: Track clinical trials with enrollment status
- 🎨 **Beautiful UI**: Dark theme with neon aesthetics and custom animations
- 📱 **Responsive Design**: Works on all device sizes
- 🔐 **Secure Database**: Supabase backend with Row Level Security

## Tech Stack

- **Frontend**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + shadcn/ui components
- **Database**: Supabase (PostgreSQL)
- **Language**: TypeScript
- **Fonts**: JetBrains Mono + Crimson Pro

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Supabase account (free tier works)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up Supabase:

   - Create a new Supabase project at [supabase.com](https://supabase.com)
   - Run the SQL schema from `supabase/schema.sql` in your Supabase SQL editor
   - Copy your project URL and anon key

3. Configure environment variables:
   - Copy `.env.example` to `.env.local`
   - Add your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

4. Run the development server:

```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
app/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles with custom theme
│   ├── layout.tsx         # Root layout with fonts
│   └── page.tsx           # Main dashboard page
├── components/ui/         # shadcn/ui components
├── lib/                   # Utilities and Supabase client
├── types/                 # TypeScript type definitions
└── supabase/             # Database schema
```

## Database Schema

The application uses two main tables:

### Patients Table

- Patient demographics (name, age, date of birth, gender)
- Contact information (email, phone)
- Location and medical history
- Diagnosed conditions and current medications
- Trial eligibility tracking (JSONB fields)

### Trials Table

- Trial information (title, phase, condition)
- Study location and timeline (start/end dates)
- Sponsor information
- Eligible patient tracking (JSONB fields)

## Key Features Implementation

### Beautiful Dark Theme

- Custom CSS variables for consistent theming
- Gradient accents and glow effects
- Smooth animations with staggered delays
- Pattern background for depth

### Real-time Data

- Supabase real-time subscriptions (can be added)
- Automatic data refresh on mutations
- Optimistic UI updates

### Search & Filter

- Client-side search for instant results
- Filter by multiple criteria
- Export functionality (to be implemented)

## Deployment

### Deploy to Vercel

1. Push your code to GitHub
2. Import project to Vercel
3. Add environment variables
4. Deploy!

### Deploy to Other Platforms

The app can be deployed to any platform that supports Next.js:

- Netlify
- Railway
- AWS Amplify
- Self-hosted with Docker

## Contributing

Feel free to submit issues and pull requests!

## License

MIT
