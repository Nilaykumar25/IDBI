# Storage Module

This module provides the database persistence layer for the MSME Financial Health Score system.

## Components

### ScoreHistoryStore

Manages persistence and retrieval of score computation results.

**Features:**
- Save score computation results to Supabase
- Retrieve most recent score by MSME ID
- Retrieve historical scores with date range filtering
- Default 6-month history retrieval for Trend Analysis View
- Count records and list unique MSME IDs

**Usage:**

```python
from storage import ScoreHistoryStore
from datetime import datetime, timedelta

# Initialize store (reads SUPABASE_URL and SUPABASE_KEY from config)
store = ScoreHistoryStore()

# Save a score result
score_result = {
    'msme_id': 'MSME-12345',
    'composite_score': 75.5,
    'risk_band': 'Low',
    'ml_confidence': {
        'low': 0.85,
        'medium': 0.12,
        'high': 0.03
    },
    'features': {
        'revenue_stability': 0.88,
        'transaction_velocity': 0.72,
        'liquidity_ratio': 0.90,
        'employment_consistency': 0.65,
        'compliance_score': 0.95,
        'growth_indicator': 0.68
    },
    'shap_values': {
        'revenue_stability': 0.15,
        'transaction_velocity': 0.08,
        'liquidity_ratio': 0.12,
        'employment_consistency': -0.02,
        'compliance_score': 0.18,
        'growth_indicator': 0.05
    },
    'missing_sources': [],
    'sector': 'Trader'
}

saved_record = store.save(score_result)
print(f"Saved with ID: {saved_record['id']}")

# Retrieve most recent score
recent_score = store.retrieve('MSME-12345')
if recent_score:
    print(f"Score: {recent_score['composite_score']}")
    print(f"Risk Band: {recent_score['risk_band']}")
else:
    print("No score found")

# Retrieve 6 months of history (default)
history = store.retrieve_history('MSME-12345')
print(f"Found {len(history)} historical records")

# Retrieve custom date range
start_date = datetime.now() - timedelta(days=90)  # Last 3 months
end_date = datetime.now()
history = store.retrieve_history('MSME-12345', start_date, end_date)

# Get all MSME IDs with score history
all_msmes = store.get_all_msme_ids()
print(f"Total MSMEs tracked: {len(all_msmes)}")

# Count records
total_records = store.count_records()
msme_records = store.count_records(msme_id='MSME-12345')
print(f"Total: {total_records}, MSME-12345: {msme_records}")
```

### ScoreHistoryArchival

Manages retention policy and archival operations.

**Features:**
- Identify records eligible for archival (>12 months old)
- Archive old records with dry-run support
- Enforce 6-month minimum retention policy
- Generate storage statistics

**Usage:**

```python
from storage import ScoreHistoryArchival

# Initialize archival manager
archival = ScoreHistoryArchival()

# Get storage statistics
stats = archival.get_storage_stats()
print(f"Total records: {stats['total_records']}")
print(f"Unique MSMEs: {stats['unique_msmes']}")
print(f"Records older than 12 months: {stats['records_older_than_12_months']}")

# Check retention policy compliance
retention_check = archival.enforce_minimum_retention(min_months=6)
if retention_check['compliant']:
    print("✓ All MSMEs have at least 6 months of history")
else:
    print(f"⚠ {len(retention_check['non_compliant_msmes'])} MSMEs lack 6 months of history")

# Dry run archival (no changes)
result = archival.archive_old_records(months=12, dry_run=True)
print(f"Would archive {result['records_found']} records")

# Actually archive old records
result = archival.archive_old_records(months=12, dry_run=False)
print(f"Archived {result['records_archived']} records")
```

## CLI Tools

### Archival Management Script

Use `scripts/manage_archival.py` for manual archival operations:

```bash
# Check storage statistics
python backend/scripts/manage_archival.py --storage-stats

# Check retention compliance
python backend/scripts/manage_archival.py --check-retention

# Preview archival (dry run)
python backend/scripts/manage_archival.py --archive --dry-run

# Archive records older than 12 months
python backend/scripts/manage_archival.py --archive --months 12

# Archive records older than 18 months
python backend/scripts/manage_archival.py --archive --months 18
```

## Database Schema

### score_history Table

```sql
CREATE TABLE score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    msme_id TEXT NOT NULL,
    composite_score NUMERIC(5,2) NOT NULL,
    risk_band TEXT NOT NULL,
    ml_confidence_low NUMERIC(5,4),
    ml_confidence_medium NUMERIC(5,4),
    ml_confidence_high NUMERIC(5,4),
    features JSONB NOT NULL,
    shap_values JSONB NOT NULL,
    missing_sources TEXT[],
    computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sector TEXT NOT NULL
);
```

**Indexes:**
- `idx_msme_computed` on (msme_id, computed_at DESC)
- `idx_computed_at` on (computed_at)

**Row Level Security:**
- Authenticated users: Read and insert access
- Service role: Full access

## Retention Policy

The storage layer implements a 6-12 month retention policy:

- **Minimum retention**: 6 months (required for Trend Analysis View)
- **Recommended retention**: 12 months in active storage
- **Archival threshold**: Records older than 12 months

### Retention Enforcement

The system ensures compliance with the 6-month minimum retention:

```python
# Check compliance
archival = ScoreHistoryArchival()
check = archival.enforce_minimum_retention(min_months=6)

if not check['compliant']:
    print(f"Warning: {len(check['non_compliant_msmes'])} MSMEs have < 6 months history")
    for msme_id in check['non_compliant_msmes']:
        print(f"  - {msme_id}")
```

### Automated Archival (Production)

For production environments, set up automated archival using Supabase Database Functions or pg_cron:

```sql
-- Create archival function
CREATE OR REPLACE FUNCTION archive_old_scores()
RETURNS void AS $$
BEGIN
    DELETE FROM score_history 
    WHERE computed_at < NOW() - INTERVAL '12 months';
END;
$$ LANGUAGE plpgsql;

-- Schedule monthly execution (requires pg_cron)
SELECT cron.schedule(
    'monthly-archival',
    '0 2 1 * *',  -- 2 AM on 1st of each month
    'SELECT archive_old_scores();'
);
```

## Error Handling

All storage operations include comprehensive error handling:

```python
from storage import ScoreHistoryStore

store = ScoreHistoryStore()

try:
    result = store.save(score_result)
except ValueError as e:
    # Missing required fields
    print(f"Validation error: {e}")
except Exception as e:
    # Database operation failed
    print(f"Database error: {e}")
```

## Testing

Run the test suite to verify database operations:

```bash
# Run all storage tests
pytest backend/test_score_history_store.py -v

# Run specific test
pytest backend/test_score_history_store.py::test_save_score_result -v
```

Note: Tests require `SUPABASE_URL` and `SUPABASE_KEY` in `.env` to run database operations.

## Configuration

Storage components read configuration from environment variables via `config.py`:

```python
# .env file
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

## Next Steps

After setting up the storage layer:

1. ✅ Database table created (`migrations/create_score_history_table.sql`)
2. ✅ ScoreHistoryStore implemented
3. ✅ Archival logic implemented
4. ➡️ Integrate with ScoringEngine (Task 8)
5. ➡️ Implement API endpoints that persist scores (Task 10)
6. ➡️ Build frontend Trend Analysis View that queries history (Task 14.3)

## Additional Resources

- [DATABASE_SETUP.md](../DATABASE_SETUP.md) - Complete database setup guide
- [Supabase Python Client Docs](https://github.com/supabase-community/supabase-py)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
