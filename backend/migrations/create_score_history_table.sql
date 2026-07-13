-- Migration: Create score_history table for MSME Financial Health Score system
-- Description: Stores historical score computations with 6-12 month retention policy
-- Technology: PostgreSQL 14+ (Supabase)

-- Create score_history table
CREATE TABLE IF NOT EXISTS score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    msme_id TEXT NOT NULL,
    composite_score NUMERIC(5,2) NOT NULL CHECK (composite_score >= 0 AND composite_score <= 100),
    risk_band TEXT NOT NULL CHECK (risk_band IN ('Low', 'Medium', 'High')),
    ml_confidence_low NUMERIC(5,4),
    ml_confidence_medium NUMERIC(5,4),
    ml_confidence_high NUMERIC(5,4),
    features JSONB NOT NULL,
    shap_values JSONB NOT NULL,
    missing_sources TEXT[],
    computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sector TEXT NOT NULL CHECK (sector IN ('Trader', 'Manufacturer', 'Services'))
);

-- Create indexes for optimal query performance
-- Primary index: Optimizes trend queries by MSME ID
CREATE INDEX IF NOT EXISTS idx_msme_computed ON score_history (msme_id, computed_at DESC);

-- Secondary index: Optimizes date-range queries
CREATE INDEX IF NOT EXISTS idx_computed_at ON score_history (computed_at);

-- Enable Row Level Security (RLS)
ALTER TABLE score_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Allow authenticated users to read all score history
CREATE POLICY "Allow authenticated read access" ON score_history
    FOR SELECT
    TO authenticated
    USING (true);

-- RLS Policy: Allow authenticated users to insert score history
CREATE POLICY "Allow authenticated insert access" ON score_history
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- RLS Policy: Service role has full access (for backend operations)
CREATE POLICY "Service role has full access" ON score_history
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE score_history IS 'Stores MSME financial health score computations with 6-month minimum retention';
COMMENT ON COLUMN score_history.msme_id IS 'MSME identifier for tracking score history';
COMMENT ON COLUMN score_history.composite_score IS 'Weighted composite score (0-100)';
COMMENT ON COLUMN score_history.risk_band IS 'ML classifier risk classification: Low, Medium, or High';
COMMENT ON COLUMN score_history.features IS 'JSONB object containing normalized feature values (0-1)';
COMMENT ON COLUMN score_history.shap_values IS 'JSONB object containing SHAP explainability values';
COMMENT ON COLUMN score_history.missing_sources IS 'Array of data sources that failed during computation';
COMMENT ON COLUMN score_history.computed_at IS 'Timestamp of score computation';
COMMENT ON COLUMN score_history.sector IS 'MSME business type: Trader, Manufacturer, or Services';

-- Retention Policy Notes:
-- - Minimum retention: 6 months (required for Trend Analysis View)
-- - Recommended retention: 12 months active storage
-- - Archival strategy: Move records older than 12 months to cold storage
-- - Implementation: Use Supabase Database Webhooks or pg_cron for automated archival
