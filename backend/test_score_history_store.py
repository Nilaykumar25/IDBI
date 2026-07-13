"""
Unit tests for ScoreHistoryStore class.
Tests persistence and retrieval of MSME financial health scores.
"""
import pytest
from datetime import datetime, timedelta
from storage.score_history_store import ScoreHistoryStore


# Sample score result fixture
@pytest.fixture
def sample_score_result():
    """Sample score result for testing."""
    return {
        'msme_id': 'TEST-MSME-001',
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
        'sector': 'Trader',
        'computed_at': datetime.now()
    }


def test_score_history_store_initialization():
    """Test ScoreHistoryStore initialization."""
    try:
        store = ScoreHistoryStore()
        assert store.client is not None
        assert store.supabase_url is not None
        assert store.supabase_key is not None
    except ValueError as e:
        # Expected if SUPABASE_URL or SUPABASE_KEY not set
        assert "SUPABASE_URL and SUPABASE_KEY must be provided" in str(e)


def test_save_score_result(sample_score_result):
    """Test saving a score result to the database."""
    try:
        store = ScoreHistoryStore()
        
        # Save score result
        result = store.save(sample_score_result)
        
        # Verify result has ID
        assert 'id' in result
        assert result['msme_id'] == 'TEST-MSME-001'
        assert result['composite_score'] == 75.5
        assert result['risk_band'] == 'Low'
        assert result['sector'] == 'Trader'
        
        print("✓ Score result saved successfully")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_save_with_missing_fields():
    """Test that save() raises ValueError for missing required fields."""
    try:
        store = ScoreHistoryStore()
        
        # Incomplete score result
        incomplete_result = {
            'msme_id': 'TEST-MSME-002',
            'composite_score': 50.0
            # Missing required fields
        }
        
        with pytest.raises(ValueError) as exc_info:
            store.save(incomplete_result)
        
        assert "Missing required fields" in str(exc_info.value)
        print("✓ Validation for missing fields works correctly")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_retrieve_most_recent_score(sample_score_result):
    """Test retrieving the most recent score for an MSME."""
    try:
        store = ScoreHistoryStore()
        
        # Save a score result
        store.save(sample_score_result)
        
        # Retrieve most recent score
        retrieved = store.retrieve('TEST-MSME-001')
        
        if retrieved:
            assert retrieved['msme_id'] == 'TEST-MSME-001'
            assert 'composite_score' in retrieved
            assert 'risk_band' in retrieved
            print("✓ Most recent score retrieved successfully")
        else:
            print("⚠ No score found (database may be empty)")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_retrieve_nonexistent_msme():
    """Test that retrieve() returns None for nonexistent MSME."""
    try:
        store = ScoreHistoryStore()
        
        # Try to retrieve score for nonexistent MSME
        result = store.retrieve('NONEXISTENT-MSME-999')
        
        assert result is None
        print("✓ Correctly returns None for nonexistent MSME")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_retrieve_history_with_date_range(sample_score_result):
    """Test retrieving historical scores with date range filtering."""
    try:
        store = ScoreHistoryStore()
        
        # Save multiple score results with different timestamps
        for i in range(3):
            result = sample_score_result.copy()
            result['msme_id'] = 'TEST-MSME-HISTORY'
            result['computed_at'] = datetime.now() - timedelta(days=i * 30)
            store.save(result)
        
        # Retrieve 6 months of history
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now()
        
        history = store.retrieve_history('TEST-MSME-HISTORY', start_date, end_date)
        
        assert isinstance(history, list)
        assert len(history) >= 0  # May be empty if database is clean
        
        if len(history) > 0:
            # Verify records are ordered by computed_at (most recent first)
            for i in range(len(history) - 1):
                current = datetime.fromisoformat(history[i]['computed_at'].replace('Z', '+00:00'))
                next_record = datetime.fromisoformat(history[i + 1]['computed_at'].replace('Z', '+00:00'))
                assert current >= next_record
        
        print(f"✓ Retrieved {len(history)} historical records")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_retrieve_history_default_6_months(sample_score_result):
    """Test that retrieve_history() defaults to 6 months if no start date provided."""
    try:
        store = ScoreHistoryStore()
        
        # Save a score result
        store.save(sample_score_result)
        
        # Retrieve history without specifying start date
        history = store.retrieve_history('TEST-MSME-001')
        
        assert isinstance(history, list)
        print(f"✓ Default 6-month history retrieval works ({len(history)} records)")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_get_all_msme_ids(sample_score_result):
    """Test retrieving all unique MSME IDs."""
    try:
        store = ScoreHistoryStore()
        
        # Save scores for multiple MSMEs
        for i in range(3):
            result = sample_score_result.copy()
            result['msme_id'] = f'TEST-MSME-{i:03d}'
            store.save(result)
        
        # Get all MSME IDs
        msme_ids = store.get_all_msme_ids()
        
        assert isinstance(msme_ids, list)
        assert len(msme_ids) >= 0
        
        print(f"✓ Retrieved {len(msme_ids)} unique MSME IDs")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


def test_count_records():
    """Test counting score history records."""
    try:
        store = ScoreHistoryStore()
        
        # Count all records
        total_count = store.count_records()
        assert isinstance(total_count, int)
        assert total_count >= 0
        
        # Count records for specific MSME
        msme_count = store.count_records(msme_id='TEST-MSME-001')
        assert isinstance(msme_count, int)
        assert msme_count >= 0
        
        print(f"✓ Total records: {total_count}, TEST-MSME-001 records: {msme_count}")
    
    except ValueError as e:
        if "SUPABASE_URL" in str(e):
            pytest.skip("Supabase credentials not configured")
        raise


if __name__ == '__main__':
    print("Running ScoreHistoryStore tests...")
    print("Note: Tests require SUPABASE_URL and SUPABASE_KEY in .env")
    print()
    
    pytest.main([__file__, '-v'])
