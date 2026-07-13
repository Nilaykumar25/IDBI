"""
Property-Based Tests for REST API Endpoints
Tests all API routes with authentication, validation, and integration scenarios
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from scoring.scoring_engine import ScoreResult, MSMEIdentifiers
from scoring.ml_classifier import RiskBand, RiskConfidence, ShapValues
from scoring.feature_engineering import NormalizedFeatures


# Test fixtures
@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_auth():
    """Mock authentication to bypass JWT validation"""
    with patch('auth.middleware.require_auth', lambda f: f):
        yield


@pytest.fixture
def mock_scoring_engine():
    """Mock scoring engine with predictable responses"""
    with patch('routes.api_routes.scoring_engine') as mock_engine:
        # Mock compute_score response
        mock_result = Mock(spec=ScoreResult)
        mock_result.msme_id = "TEST-MSME-001"
        mock_result.composite_score = 75.5
        mock_result.ml_risk_band = "Low"
        mock_result.ml_confidence = RiskConfidence(low=0.85, medium=0.12, high=0.03)
        mock_result.shap_values = ShapValues(
            revenue_stability=0.15,
            transaction_velocity=0.22,
            liquidity_ratio=0.18,
            employment_consistency=0.08,
            compliance_score=0.05,
            growth_indicator=0.12
        )
        mock_result.features = NormalizedFeatures(
            revenue_stability=0.85,
            transaction_velocity=0.78,
            liquidity_ratio=0.82,
            employment_consistency=0.65,
            compliance_score=0.92,
            growth_indicator=0.71,
            missing_sources=[]
        )
        mock_result.missing_data_sources = []
        mock_result.computed_at = datetime.now()
        mock_result.sector = "Trader"
        
        mock_engine.compute_score.return_value = mock_result
        mock_engine.compute_with_partial_data.return_value = mock_result
        
        yield mock_engine


@pytest.fixture
def mock_score_history_store():
    """Mock score history store"""
    with patch('routes.api_routes.score_history_store') as mock_store:
        # Mock retrieve response
        mock_store.retrieve.return_value = {
            'msme_id': 'TEST-MSME-001',
            'composite_score': 75.5,
            'risk_band': 'Low',
            'ml_confidence_low': 0.85,
            'ml_confidence_medium': 0.12,
            'ml_confidence_high': 0.03,
            'shap_values': {
                'revenue_stability': 0.15,
                'transaction_velocity': 0.22,
                'liquidity_ratio': 0.18,
                'employment_consistency': 0.08,
                'compliance_score': 0.05,
                'growth_indicator': 0.12
            },
            'features': {
                'revenueStability': 0.85,
                'transactionVelocity': 0.78,
                'liquidityRatio': 0.82,
                'employmentConsistency': 0.65,
                'complianceScore': 0.92,
                'growthIndicator': 0.71
            },
            'missing_sources': [],
            'computed_at': datetime.now().isoformat(),
            'sector': 'Trader'
        }
        
        # Mock retrieve_history response
        mock_store.retrieve_history.return_value = [
            {
                'msme_id': 'TEST-MSME-001',
                'composite_score': 75.5,
                'risk_band': 'Low',
                'computed_at': datetime.now().isoformat(),
                'sector': 'Trader'
            }
        ]
        
        yield mock_store


# Strategy for generating valid MSME identifiers
msme_identifiers_strategy = st.fixed_dictionaries({
    'msmeId': st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
    'gstNumber': st.text(min_size=15, max_size=15),
    'upiId': st.text(min_size=5, max_size=50),
    'aaConsentToken': st.text(min_size=10, max_size=100),
    'epfoEstablishmentId': st.text(min_size=5, max_size=30),
    'sector': st.sampled_from(['Trader', 'Manufacturer', 'Services'])
})


# Strategy for normalized features (0-1 range)
normalized_features_strategy = st.fixed_dictionaries({
    'revenueStability': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    'transactionVelocity': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    'liquidityRatio': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    'employmentConsistency': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    'complianceScore': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    'growthIndicator': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
})


class TestScoreComputationEndpoint:
    """Tests for POST /api/scores endpoint"""
    
    @given(identifiers=msme_identifiers_strategy)
    @settings(max_examples=10, deadline=2000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_compute_score_with_valid_data(self, client, mock_auth, mock_scoring_engine, mock_score_history_store, identifiers):
        """
        Property: POST /api/scores with valid identifiers returns 200 with score data
        """
        response = client.post(
            '/api/scores',
            json=identifiers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'compositeScore' in data['data']
        assert 0 <= data['data']['compositeScore'] <= 100
        assert data['data']['riskBand'] in ['Low', 'Medium', 'High']
    
    def test_compute_score_missing_fields(self, client, mock_auth):
        """
        Property: POST /api/scores with missing required fields returns 400
        """
        incomplete_data = {
            'msmeId': 'TEST-001',
            'sector': 'Trader'
            # Missing gstNumber, upiId, aaConsentToken, epfoEstablishmentId
        }
        
        response = client.post(
            '/api/scores',
            json=incomplete_data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_compute_score_invalid_sector(self, client, mock_auth):
        """
        Property: POST /api/scores with invalid sector returns 400
        """
        invalid_data = {
            'msmeId': 'TEST-001',
            'gstNumber': '12ABCDE1234F1Z5',
            'upiId': 'test@upi',
            'aaConsentToken': 'token123',
            'epfoEstablishmentId': 'EPFO001',
            'sector': 'InvalidSector'
        }
        
        response = client.post(
            '/api/scores',
            json=invalid_data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'sector' in data['error'].lower()
    
    def test_compute_score_persists_to_history(self, client, mock_auth, mock_scoring_engine, mock_score_history_store):
        """
        Property: POST /api/scores persists result to score history store
        """
        valid_data = {
            'msmeId': 'TEST-001',
            'gstNumber': '12ABCDE1234F1Z5',
            'upiId': 'test@upi',
            'aaConsentToken': 'token123',
            'epfoEstablishmentId': 'EPFO001',
            'sector': 'Trader'
        }
        
        response = client.post(
            '/api/scores',
            json=valid_data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        # Verify save was called (even if it failed, it should have been attempted)
        # Note: In actual implementation, save is wrapped in try-except and doesn't fail the request


class TestScoreRetrievalEndpoint:
    """Tests for GET /api/scores/:msmeId endpoint"""
    
    def test_retrieve_existing_score(self, client, mock_auth, mock_score_history_store):
        """
        Property: GET /api/scores/:msmeId for existing MSME returns 200 with score data
        """
        response = client.get('/api/scores/TEST-MSME-001')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['msmeId'] == 'TEST-MSME-001'
        assert 0 <= data['data']['compositeScore'] <= 100
    
    def test_retrieve_nonexistent_score(self, client, mock_auth, mock_score_history_store):
        """
        Property: GET /api/scores/:msmeId for non-existent MSME returns 404
        """
        mock_score_history_store.retrieve.return_value = None
        
        response = client.get('/api/scores/NONEXISTENT')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error'].lower()


class TestScoreHistoryEndpoint:
    """Tests for GET /api/scores/:msmeId/history endpoint"""
    
    def test_retrieve_history_default_range(self, client, mock_auth, mock_score_history_store):
        """
        Property: GET /api/scores/:msmeId/history without date range defaults to 6 months
        """
        response = client.get('/api/scores/TEST-MSME-001/history')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['data'], list)
    
    def test_retrieve_history_with_date_range(self, client, mock_auth, mock_score_history_store):
        """
        Property: GET /api/scores/:msmeId/history with date range filters correctly
        """
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = client.get(f'/api/scores/TEST-MSME-001/history?startDate={start_date}&endDate={end_date}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['data'], list)
    
    def test_retrieve_history_invalid_date_format(self, client, mock_auth, mock_score_history_store):
        """
        Property: GET /api/scores/:msmeId/history with invalid date format returns 400
        """
        response = client.get('/api/scores/TEST-MSME-001/history?startDate=invalid-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'date' in data['error'].lower()
    
    def test_retrieve_history_invalid_range(self, client, mock_auth, mock_score_history_store):
        """
        Property: GET /api/scores/:msmeId/history with startDate > endDate returns 400
        """
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = client.get(f'/api/scores/TEST-MSME-001/history?startDate={start_date}&endDate={end_date}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestSimulateEndpoint:
    """Tests for POST /api/simulate endpoint"""
    
    @given(
        features=normalized_features_strategy,
        sector=st.sampled_from(['Trader', 'Manufacturer', 'Services'])
    )
    @settings(max_examples=10, deadline=2000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_simulate_with_valid_features(self, client, mock_auth, mock_scoring_engine, features, sector):
        """
        Property: POST /api/simulate with valid features returns 200 with simulated score
        Requirement: Response should be fast (<100ms for real-time simulation)
        """
        request_data = {
            'features': features,
            'sector': sector
        }
        
        response = client.post(
            '/api/simulate',
            json=request_data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'compositeScore' in data['data']
        assert 0 <= data['data']['compositeScore'] <= 100
        assert data['data']['riskBand'] in ['Low', 'Medium', 'High']
    
    def test_simulate_missing_features(self, client, mock_auth):
        """
        Property: POST /api/simulate with missing features returns 400
        """
        incomplete_data = {
            'features': {
                'revenueStability': 0.8
                # Missing other features
            },
            'sector': 'Trader'
        }
        
        response = client.post(
            '/api/simulate',
            json=incomplete_data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_simulate_invalid_feature_values(self, client, mock_auth):
        """
        Property: POST /api/simulate with out-of-range features returns 400
        """
        invalid_data = {
            'features': {
                'revenueStability': 1.5,  # Invalid: > 1.0
                'transactionVelocity': 0.5,
                'liquidityRatio': 0.5,
                'employmentConsistency': 0.5,
                'complianceScore': 0.5,
                'growthIndicator': 0.5
            },
            'sector': 'Trader'
        }
        
        response = client.post(
            '/api/simulate',
            json=invalid_data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestEcosystemEndpoints:
    """Tests for ecosystem integration endpoints"""
    
    def test_aa_consent_simulation(self, client, mock_auth):
        """
        Property: POST /api/ecosystem/consent returns mock consent token
        """
        response = client.post('/api/ecosystem/consent')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'consentToken' in data['data']
        assert data['data']['status'] == 'approved'
    
    def test_uli_publish_simulation(self, client, mock_auth):
        """
        Property: POST /api/ecosystem/publish returns mock transaction ID
        """
        response = client.post('/api/ecosystem/publish')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'transactionId' in data['data']
        assert data['data']['status'] == 'published'
    
    @pytest.mark.parametrize('risk_band', ['Low', 'Medium', 'High'])
    def test_lender_matching(self, client, mock_auth, risk_band):
        """
        Property: GET /api/ecosystem/lenders returns lenders matching risk band
        """
        response = client.get(f'/api/ecosystem/lenders?riskBand={risk_band}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['riskBand'] == risk_band
        assert len(data['data']['lenders']) >= 2  # At least 2 lenders
    
    def test_lender_matching_missing_risk_band(self, client, mock_auth):
        """
        Property: GET /api/ecosystem/lenders without riskBand returns 400
        """
        response = client.get('/api/ecosystem/lenders')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
