# Supabase Setup Guide

This guide walks you through setting up Supabase for the MSME Financial Health Score system.

## Step 1: Create a Supabase Account

1. Go to [https://app.supabase.com/](https://app.supabase.com/)
2. Click "Start your project"
3. Sign up with GitHub, Google, or email

## Step 2: Create a New Project

1. Click "New Project"
2. Fill in the project details:
   - **Name**: `msme-financial-health` (or your preferred name)
   - **Database Password**: Choose a strong password (save it securely)
   - **Region**: Choose the closest region to your location
   - **Pricing Plan**: Free tier is sufficient for development
3. Click "Create new project"
4. Wait 2-3 minutes for the project to be provisioned

## Step 3: Enable Email/Password Authentication

1. In your project dashboard, navigate to **Authentication** in the left sidebar
2. Click on **Providers**
3. Find **Email** in the list and ensure it's enabled (it should be enabled by default)
4. (Optional) Configure email settings:
   - For development, you can use the default Supabase email service
   - For production, configure a custom SMTP provider under **Authentication → Settings → SMTP Settings**

### Email Confirmation Settings

By default, Supabase requires email confirmation for new signups. For development, you can disable this:

1. Go to **Authentication → Policies**
2. Under **Email Auth**, toggle "Enable email confirmations" to OFF
3. This allows immediate login after signup without email verification

**Note**: Re-enable email confirmation for production deployments.

## Step 4: Obtain API Credentials

### Get Project URL and API Key

1. Navigate to **Project Settings** (gear icon in the left sidebar)
2. Click on **API** in the settings menu
3. You'll see the following credentials:

   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **API Keys**:
     - **anon/public key**: Starts with `eyJ...` (this is safe to use in frontend)
     - **service_role key**: Also starts with `eyJ...` (keep this secret, used only in backend if needed)

4. Copy the **Project URL** and **anon public key**

### Get JWT Secret

1. Still in **Project Settings → API**
2. Scroll down to **JWT Settings**
3. Copy the **JWT Secret** (used for backend token verification)

## Step 5: Configure Your Application

### Backend Configuration

Edit `backend/.env`:

```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon/public key
SUPABASE_JWT_SECRET=your-jwt-secret-here

ADAPTER_MODE=mock
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
PORT=5000
CORS_ORIGINS=http://localhost:3000
```

### Frontend Configuration

Edit `frontend/.env`:

```bash
VITE_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon/public key
VITE_API_URL=http://localhost:5000/api
```

## Step 6: Test Authentication

1. Start your backend:
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   python app.py
   ```

2. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open http://localhost:3000
4. Click "Sign up" and create a test account
5. You should be logged in and redirected to the dashboard

## Step 7: (Optional) Set Up Database Tables

For Task 9 (database layer for score history), you'll need to create the `score_history` table:

1. Navigate to **SQL Editor** in your Supabase dashboard
2. Click **New query**
3. Paste the following SQL:

```sql
CREATE TABLE score_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  msme_id VARCHAR(100) NOT NULL,
  composite_score DECIMAL(5,2) NOT NULL CHECK (composite_score >= 0 AND composite_score <= 100),
  risk_band VARCHAR(10) NOT NULL CHECK (risk_band IN ('Low', 'Medium', 'High')),
  ml_confidence_low DECIMAL(5,4),
  ml_confidence_medium DECIMAL(5,4),
  ml_confidence_high DECIMAL(5,4),
  features JSONB NOT NULL,
  shap_values JSONB NOT NULL,
  missing_sources TEXT[],
  computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  sector VARCHAR(20) NOT NULL
);

CREATE INDEX idx_msme_computed ON score_history (msme_id, computed_at DESC);
CREATE INDEX idx_computed_at ON score_history (computed_at);
```

4. Click **Run**

**Note**: This step is only needed for Task 9. Task 1 only requires authentication to be set up.

## Step 8: (Optional) Enable Row Level Security (Production)

For production deployments, enable Row Level Security (RLS) on the `score_history` table:

1. Go to **Authentication → Policies**
2. Enable RLS on the `score_history` table
3. Add policies to control data access based on authenticated users

**Note**: RLS is not required for development with mock data.

## Troubleshooting

### "Invalid API key" errors

- Double-check that you copied the **anon/public key**, not the service_role key
- Ensure there are no extra spaces or line breaks in the `.env` files
- Verify the key starts with `eyJ`

### "Failed to fetch" errors

- Check that your Supabase project is active (green status indicator)
- Verify the Project URL is correct and includes `https://`
- Check your internet connection

### Email confirmation blocking signups

- Go to **Authentication → Policies** and disable "Enable email confirmations"
- Or check your email for the confirmation link

### CORS errors

- Ensure your Supabase project allows requests from `http://localhost:3000`
- This should be enabled by default for development

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

## Need Help?

If you encounter issues:

1. Check the [Supabase Status Page](https://status.supabase.com/)
2. Review the browser console for error messages
3. Check backend logs for authentication errors
4. Verify environment variables are correctly set in both `.env` files
