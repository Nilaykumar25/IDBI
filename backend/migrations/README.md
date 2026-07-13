# Database Migrations

This directory contains SQL migration scripts for the MSME Financial Health Score system.

## Running Migrations

### Option 1: Supabase SQL Editor (Recommended for Development)

1. Log in to your Supabase dashboard: https://app.supabase.com
2. Navigate to your project
3. Go to **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy the contents of `create_score_history_table.sql`
6. Paste into the editor and click **Run**

### Option 2: Supabase CLI (Recommended for Production)

```bash
# Install Supabase CLI
npm install -g supabase

# Link your project
supabase link --project-ref <your-project-ref>

# Run migration
supabase db push
```

### Option 3: psql Command Line

```bash
# Connect to your Supabase database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run migration
\i backend/migrations/create_score_history_table.sql
```

## Migration Files

### `create_score_history_table.sql`

Creates the `score_history` table with:
- Primary key: `id` (UUID)
- MSME identifier: `msme_id` (TEXT)
- Score fields: `composite_score`, `risk_band`, ML confidence scores
- Feature data: `features` (JSONB), `shap_values` (JSONB)
- Metadata: `missing_sources`, `computed_at`, `sector`
- Indexes: Optimized for MSME trend queries and date-range filtering
- Row Level Security: Enabled with policies for authenticated users

## Verification

After running migrations, verify the table was created:

```sql
-- Check table exists
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'score_history';

-- Check indexes
SELECT indexname, indexdef FROM pg_indexes 
WHERE tablename = 'score_history';

-- Check RLS policies
SELECT policyname, permissive, roles, cmd FROM pg_policies 
WHERE tablename = 'score_history';
```

## Retention Policy

The `score_history` table implements a 6-12 month retention policy:
- **Minimum retention**: 6 months (required for Trend Analysis View)
- **Active storage**: 12 months recommended
- **Archival**: Records older than 12 months should be moved to cold storage

### Implementing Automated Archival

Use Supabase Database Webhooks or pg_cron for automated archival:

```sql
-- Example: Archive records older than 12 months (run monthly)
-- This would be set up as a scheduled function in Supabase
CREATE OR REPLACE FUNCTION archive_old_scores()
RETURNS void AS $$
BEGIN
    -- Move to archive table (create this table separately)
    INSERT INTO score_history_archive 
    SELECT * FROM score_history 
    WHERE computed_at < NOW() - INTERVAL '12 months';
    
    -- Delete from active table
    DELETE FROM score_history 
    WHERE computed_at < NOW() - INTERVAL '12 months';
END;
$$ LANGUAGE plpgsql;
```
