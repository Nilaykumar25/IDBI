# Database Setup Guide

This guide walks you through setting up the Supabase database for the MSME Financial Health Score system.

## Prerequisites

- Supabase account (sign up at https://supabase.com)
- Supabase project created
- SUPABASE_URL and SUPABASE_KEY from your project settings

## Quick Setup

### 1. Create Supabase Project

If you haven't already:

1. Go to https://app.supabase.com
2. Click "New Project"
3. Enter project name: `msme-financial-health-score`
4. Choose a database password (save this securely)
5. Select a region closest to your users
6. Wait for project initialization (~2 minutes)

### 2. Get Your Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following:
   - **Project URL**: This is your `SUPABASE_URL`
   - **Project API keys** → **anon/public**: This is your `SUPABASE_KEY`
   - **JWT Secret**: This is your `SUPABASE_JWT_SECRET`

### 3. Update Environment Variables

Update `backend/.env` with your credentials:

```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

### 4. Run Database Migration

#### Option A: Supabase SQL Editor (Recommended)

1. Open your Supabase dashboard
2. Go to **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire contents of `backend/migrations/create_score_history_table.sql`
5. Paste into the editor
6. Click **Run** (or press Ctrl/Cmd + Enter)
7. Verify success message appears

#### Option B: Command Line

```bash
# Navigate to backend directory
cd backend

# Run migration using psql
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres" \
  -f migrations/create_score_history_table.sql
```

### 5. Verify Database Setup

After running the migration, verify the table was created:

```sql
-- In Supabase SQL Editor
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'score_history';
```

Expected output:
```
table_name
--------------
score_history
```

Verify indexes:

```sql
SELECT indexname FROM pg_indexes 
WHERE tablename = 'score_history';
```

Expected output:
```
indexname
------------------------
score_history_pkey
idx_msme_computed
idx_computed_at
```

Verify RLS policies:

```sql
SELECT policyname FROM pg_policies 
WHERE tablename = 'score_history';
```

Expected output:
```
policyname
----------------------------------
Allow authenticated read access
Allow authenticated insert access
Service role has full access
```

### 6. Test Database Connection

Run the test suite to verify everything works:

```bash
cd backend
pytest test_score_history_store.py -v
```

Expected output:
```
test_score_history_store.py::test_score_history_store_initialization PASSED
test_score_history_store.py::test_save_score_result PASSED
test_score_history_store.py::test_retrieve_most_recent_score PASSED
...
```

## Database Schema

### score_history Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Auto-generated unique identifier |
| msme_id | TEXT | NOT NULL | MSME business identifier |
| composite_score | NUMERIC(5,2) | NOT NULL, 0-100 | Weighted composite score |
| risk_band | TEXT | NOT NULL | Risk classification: Low, Medium, High |
| ml_confidence_low | NUMERIC(5,4) | - | ML confidence for Low risk |
| ml_confidence_medium | NUMERIC(5,4) | - | ML confidence for Medium risk |
| ml_confidence_high | NUMERIC(5,4) | - | ML confidence for High risk |
| features | JSONB | NOT NULL | Normalized feature values (0-1) |
| shap_values | JSONB | NOT NULL | SHAP explainability values |
| missing_sources | TEXT[] | - | Array of failed data sources |
| computed_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Score computation timestamp |
| sector | TEXT | NOT NULL | MSME sector: Trader, Manufacturer, Services |

### Indexes

- `idx_msme_computed`: (msme_id, computed_at DESC) - Optimizes trend queries
- `idx_computed_at`: (computed_at) - Optimizes date-range queries

### Row Level Security (RLS)

RLS is enabled with the following policies:

1. **Allow authenticated read access**: Authenticated users can read all score history
2. **Allow authenticated insert access**: Authenticated users can insert new scores
3. **Service role has full access**: Backend service has full CRUD permissions

## Usage Examples

### Python (Backend)

```python
from storage import ScoreHistoryStore
from datetime import datetime, timedelta

# Initialize store
store = ScoreHistoryStore()

# Save a score result
score_result = {
    'msme_id': 'MSME-12345',
    'composite_score': 75.5,
    'risk_band': 'Low',
    'ml_confidence': {'low': 0.85, 'medium': 0.12, 'high': 0.03},
    'features': {...},
    'shap_values': {...},
    'missing_sources': [],
    'sector': 'Trader'
}
saved = store.save(score_result)
print(f"Saved with ID: {saved['id']}")

# Retrieve most recent score
recent = store.retrieve('MSME-12345')
print(f"Most recent score: {recent['composite_score']}")

# Retrieve 6 months of history
start_date = datetime.now() - timedelta(days=180)
history = store.retrieve_history('MSME-12345', start_date=start_date)
print(f"Historical records: {len(history)}")
```

### JavaScript (Frontend)

```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Retrieve most recent score
const { data, error } = await supabase
  .from('score_history')
  .select('*')
  .eq('msme_id', 'MSME-12345')
  .order('computed_at', { ascending: false })
  .limit(1);

if (data && data.length > 0) {
  console.log('Most recent score:', data[0].composite_score);
}
```

## Retention Policy and Archival

The system implements a 6-12 month retention policy:

- **Minimum retention**: 6 months (required for Trend Analysis)
- **Active storage**: 12 months recommended
- **Archival**: Records older than 12 months

### Manual Archival

Use the management script for manual archival:

```bash
# Check storage statistics
python scripts/manage_archival.py --storage-stats

# Check retention compliance
python scripts/manage_archival.py --check-retention

# Dry run archival (no changes)
python scripts/manage_archival.py --archive --dry-run

# Actually archive old records
python scripts/manage_archival.py --archive --months 12
```

### Automated Archival (Optional)

For production, set up automated archival using Supabase Database Webhooks or pg_cron:

```sql
-- Example: Create scheduled function for monthly archival
CREATE OR REPLACE FUNCTION archive_old_scores()
RETURNS void AS $$
BEGIN
    -- Archive records older than 12 months
    DELETE FROM score_history 
    WHERE computed_at < NOW() - INTERVAL '12 months';
END;
$$ LANGUAGE plpgsql;

-- Schedule to run monthly (requires pg_cron extension)
SELECT cron.schedule(
    'archive-old-scores',
    '0 2 1 * *',  -- Run at 2 AM on 1st of each month
    'SELECT archive_old_scores();'
);
```

## Troubleshooting

### Error: "Missing required environment variables"

**Solution**: Verify `.env` file contains `SUPABASE_URL` and `SUPABASE_KEY`:

```bash
cat backend/.env | grep SUPABASE
```

### Error: "relation 'score_history' does not exist"

**Solution**: Run the migration SQL script in Supabase SQL Editor.

### Error: "permission denied for table score_history"

**Solution**: Verify RLS policies are correctly set up. Check policies in Supabase dashboard under **Database** → **score_history** → **Policies**.

### Error: "JWT token is invalid"

**Solution**: Verify `SUPABASE_JWT_SECRET` matches the JWT Secret in your Supabase project settings.

## Next Steps

After completing database setup:

1. ✅ Database table created
2. ✅ Indexes configured
3. ✅ RLS policies enabled
4. ➡️ Proceed to Task 10: Implement REST API endpoints
5. ➡️ Integrate ScoreHistoryStore with ScoringEngine

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
