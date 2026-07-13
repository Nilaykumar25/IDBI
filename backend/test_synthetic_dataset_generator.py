"""
Tests for Synthetic Dataset Generator
"""
import pytest
import os
import json
import csv
from scoring.synthetic_dataset_generator import (
    SyntheticDatasetGenerator,
    SyntheticProfile
)


class TestSyntheticDatasetGenerator:
    """Test suite for SyntheticDatasetGenerator"""
    
    def test_generate_low_risk_profile(self):
        """Test generation of Low risk profile with appropriate feature ranges"""
        generator = SyntheticDatasetGenerator(seed=42)
        profile = generator.generate_synthetic_profile('Low', 'Trader')
        
        # Verify basic structure
        assert profile.msme_id is not None
        assert profile.sector == 'Trader'
        assert profile.risk_band == 'Low'
        
        # Verify features are in valid range
        for feature, value in profile.features.items():
            assert 0.0 <= value <= 1.0, f"{feature} out of range: {value}"
        
        # Low risk should generally have higher feature values
        # At least 4 out of 6 features should be > 0.6
        high_features = sum(1 for v in profile.features.values() if v > 0.6)
        assert high_features >= 4, f"Low risk profile should have mostly high features, got {high_features}/6"
    
    def test_generate_high_risk_profile(self):
        """Test generation of High risk profile with appropriate feature ranges"""
        generator = SyntheticDatasetGenerator(seed=42)
        profile = generator.generate_synthetic_profile('High', 'Services')
        
        # Verify basic structure
        assert profile.msme_id is not None
        assert profile.sector == 'Services'
        assert profile.risk_band == 'High'
        
        # Verify features are in valid range
        for feature, value in profile.features.items():
            assert 0.0 <= value <= 1.0, f"{feature} out of range: {value}"
        
        # High risk should generally have lower feature values
        # At least 4 out of 6 features should be < 0.5
        low_features = sum(1 for v in profile.features.values() if v < 0.5)
        assert low_features >= 4, f"High risk profile should have mostly low features, got {low_features}/6"
    
    def test_generate_medium_risk_profile(self):
        """Test generation of Medium risk profile with mixed features"""
        generator = SyntheticDatasetGenerator(seed=42)
        profile = generator.generate_synthetic_profile('Medium', 'Manufacturer')
        
        # Verify basic structure
        assert profile.msme_id is not None
        assert profile.sector == 'Manufacturer'
        assert profile.risk_band == 'Medium'
        
        # Verify features are in valid range
        for feature, value in profile.features.items():
            assert 0.0 <= value <= 1.0, f"{feature} out of range: {value}"
        
        # Medium risk should have mixed features
        avg_feature_value = sum(profile.features.values()) / len(profile.features)
        assert 0.3 < avg_feature_value < 0.7, f"Medium risk should have moderate features, got avg {avg_feature_value}"
    
    def test_custom_msme_id(self):
        """Test generation with custom MSME ID"""
        generator = SyntheticDatasetGenerator(seed=42)
        custom_id = "CUSTOM-TEST-001"
        profile = generator.generate_synthetic_profile('Low', 'Trader', msme_id=custom_id)
        
        assert profile.msme_id == custom_id
    
    def test_feature_correlations(self):
        """Test that cross-feature correlations are applied"""
        generator = SyntheticDatasetGenerator(seed=42)
        
        # Generate many profiles and check correlations exist
        profiles = [generator.generate_synthetic_profile('Low', 'Trader') for _ in range(100)]
        
        # Check that some profiles with high revenue stability also have high compliance
        high_rev_profiles = [p for p in profiles if p.features['revenue_stability'] > 0.7]
        if high_rev_profiles:
            avg_compliance = sum(p.features['compliance_score'] for p in high_rev_profiles) / len(high_rev_profiles)
            # Should be generally higher due to correlation
            assert avg_compliance > 0.7, "High revenue stability should correlate with higher compliance"
    
    def test_generate_dataset(self):
        """Test full dataset generation with correct distribution"""
        generator = SyntheticDatasetGenerator(seed=42)
        size = 100
        profiles = generator.generate_dataset(size=size, low_pct=0.5, medium_pct=0.3, high_pct=0.2)
        
        # Verify total count
        assert len(profiles) == size
        
        # Verify distribution
        low_count = sum(1 for p in profiles if p.risk_band == 'Low')
        medium_count = sum(1 for p in profiles if p.risk_band == 'Medium')
        high_count = sum(1 for p in profiles if p.risk_band == 'High')
        
        # Allow some tolerance due to rounding
        assert 48 <= low_count <= 52, f"Expected ~50 Low risk, got {low_count}"
        assert 28 <= medium_count <= 32, f"Expected ~30 Medium risk, got {medium_count}"
        assert 18 <= high_count <= 22, f"Expected ~20 High risk, got {high_count}"
        
        # Verify sectors are distributed
        sectors = [p.sector for p in profiles]
        assert 'Trader' in sectors
        assert 'Manufacturer' in sectors
        assert 'Services' in sectors
    
    def test_generate_dataset_custom_distribution(self):
        """Test dataset generation with custom risk distribution"""
        generator = SyntheticDatasetGenerator(seed=42)
        size = 100
        profiles = generator.generate_dataset(
            size=size, 
            low_pct=0.6,  # 60%
            medium_pct=0.25,  # 25%
            high_pct=0.15  # 15%
        )
        
        # Verify distribution
        low_count = sum(1 for p in profiles if p.risk_band == 'Low')
        medium_count = sum(1 for p in profiles if p.risk_band == 'Medium')
        high_count = sum(1 for p in profiles if p.risk_band == 'High')
        
        assert 58 <= low_count <= 62, f"Expected ~60 Low risk, got {low_count}"
        assert 23 <= medium_count <= 27, f"Expected ~25 Medium risk, got {medium_count}"
        assert 13 <= high_count <= 17, f"Expected ~15 High risk, got {high_count}"
    
    def test_export_to_csv(self, tmp_path):
        """Test CSV export functionality"""
        generator = SyntheticDatasetGenerator(seed=42)
        profiles = generator.generate_dataset(size=10)
        
        csv_file = tmp_path / "test_dataset.csv"
        generator.export_to_csv(profiles, str(csv_file))
        
        # Verify file exists
        assert csv_file.exists()
        
        # Verify CSV structure
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Verify row count
            assert len(rows) == 10
            
            # Verify headers
            expected_headers = [
                'msme_id', 'sector',
                'revenue_stability', 'transaction_velocity', 'liquidity_ratio',
                'employment_consistency', 'compliance_score', 'growth_indicator',
                'risk_band'
            ]
            assert list(rows[0].keys()) == expected_headers
            
            # Verify data types and ranges
            for row in rows:
                assert row['msme_id'] != ''
                assert row['sector'] in ['Trader', 'Manufacturer', 'Services']
                assert row['risk_band'] in ['Low', 'Medium', 'High']
                
                # Check feature values are in 0-1 range
                for feature in ['revenue_stability', 'transaction_velocity', 'liquidity_ratio',
                               'employment_consistency', 'compliance_score', 'growth_indicator']:
                    value = float(row[feature])
                    assert 0.0 <= value <= 1.0, f"{feature} = {value} out of range"
    
    def test_export_to_json(self, tmp_path):
        """Test JSON export functionality"""
        generator = SyntheticDatasetGenerator(seed=42)
        profiles = generator.generate_dataset(size=10)
        
        json_file = tmp_path / "test_dataset.json"
        generator.export_to_json(profiles, str(json_file))
        
        # Verify file exists
        assert json_file.exists()
        
        # Verify JSON structure
        with open(json_file, 'r') as f:
            data = json.load(f)
            
            # Verify it's a list
            assert isinstance(data, list)
            assert len(data) == 10
            
            # Verify structure of first profile
            profile = data[0]
            assert 'msme_id' in profile
            assert 'sector' in profile
            assert 'features' in profile
            assert 'risk_band' in profile
            
            # Verify features
            features = profile['features']
            assert len(features) == 6
            for feature_name, value in features.items():
                assert 0.0 <= value <= 1.0
    
    def test_reproducibility_with_seed(self):
        """Test that using same seed produces identical results"""
        # Generate first dataset
        generator1 = SyntheticDatasetGenerator(seed=123)
        profiles1 = generator1.generate_dataset(size=50)
        
        # Generate second dataset with same seed (reset state)
        generator2 = SyntheticDatasetGenerator(seed=123)
        profiles2 = generator2.generate_dataset(size=50)
        
        # Verify identical results
        for p1, p2 in zip(profiles1, profiles2):
            assert p1.sector == p2.sector, f"Sectors differ: {p1.sector} vs {p2.sector}"
            assert p1.risk_band == p2.risk_band, f"Risk bands differ: {p1.risk_band} vs {p2.risk_band}"
            for feature in p1.features:
                assert abs(p1.features[feature] - p2.features[feature]) < 0.001, \
                    f"Feature {feature} differs: {p1.features[feature]} vs {p2.features[feature]}"
    
    def test_invalid_percentage_distribution(self):
        """Test that invalid percentage distribution raises error"""
        generator = SyntheticDatasetGenerator(seed=42)
        
        with pytest.raises(ValueError):
            generator.generate_dataset(size=100, low_pct=0.5, medium_pct=0.3, high_pct=0.3)  # Sums to 1.1
    
    def test_profile_to_dict(self):
        """Test SyntheticProfile to_dict conversion"""
        generator = SyntheticDatasetGenerator(seed=42)
        profile = generator.generate_synthetic_profile('Low', 'Trader', msme_id='TEST-001')
        
        profile_dict = profile.to_dict()
        
        assert isinstance(profile_dict, dict)
        assert profile_dict['msme_id'] == 'TEST-001'
        assert profile_dict['sector'] == 'Trader'
        assert profile_dict['risk_band'] == 'Low'
        assert isinstance(profile_dict['features'], dict)
        assert len(profile_dict['features']) == 6


class TestDemoProfiles:
    """Test suite for demo profiles fixture"""
    
    def test_demo_profiles_fixture_exists(self):
        """Test that demo profiles fixture file exists"""
        fixture_path = 'backend/fixtures/demo_profiles.json'
        assert os.path.exists(fixture_path), "Demo profiles fixture not found"
    
    def test_demo_profiles_structure(self):
        """Test that demo profiles have correct structure"""
        fixture_path = 'backend/fixtures/demo_profiles.json'
        
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        # Verify top-level structure
        assert 'profiles' in data
        assert 'metadata' in data
        
        # Verify metadata
        assert data['metadata']['total_profiles'] == 4
        
        # Verify profiles
        profiles = data['profiles']
        assert len(profiles) == 4
        
        # Check each profile has required fields
        for profile in profiles:
            assert 'msme_id' in profile
            assert 'sector' in profile
            assert 'features' in profile
            assert 'expected_risk_band' in profile
            assert 'description' in profile
            
            # Verify features
            features = profile['features']
            assert len(features) == 6
            for feature_name, value in features.items():
                assert 0.0 <= value <= 1.0, f"{feature_name} = {value} out of range"
    
    def test_demo_profile_low_risk(self):
        """Test DEMO-LOW-001 profile characteristics"""
        fixture_path = 'backend/fixtures/demo_profiles.json'
        
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        # Find DEMO-LOW-001
        low_profile = next(p for p in data['profiles'] if p['msme_id'] == 'DEMO-LOW-001')
        
        assert low_profile['sector'] == 'Trader'
        assert low_profile['expected_risk_band'] == 'Low'
        
        # Verify high feature values
        features = low_profile['features']
        assert features['revenue_stability'] >= 0.85
        assert features['liquidity_ratio'] >= 0.90
        assert features['compliance_score'] >= 0.90
    
    def test_demo_profile_high_risk(self):
        """Test DEMO-HIGH-001 profile characteristics"""
        fixture_path = 'backend/fixtures/demo_profiles.json'
        
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        # Find DEMO-HIGH-001
        high_profile = next(p for p in data['profiles'] if p['msme_id'] == 'DEMO-HIGH-001')
        
        assert high_profile['sector'] == 'Services'
        assert high_profile['expected_risk_band'] == 'High'
        
        # Verify low feature values
        features = high_profile['features']
        assert features['revenue_stability'] <= 0.25
        assert features['liquidity_ratio'] <= 0.20
        assert features['compliance_score'] <= 0.40
    
    def test_demo_profile_medium_risk(self):
        """Test DEMO-MED-001 profile characteristics"""
        fixture_path = 'backend/fixtures/demo_profiles.json'
        
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        # Find DEMO-MED-001
        med_profile = next(p for p in data['profiles'] if p['msme_id'] == 'DEMO-MED-001')
        
        assert med_profile['sector'] == 'Manufacturer'
        assert med_profile['expected_risk_band'] == 'Medium'
        
        # Verify mixed feature values
        features = med_profile['features']
        assert features['revenue_stability'] >= 0.60  # Decent
        assert features['transaction_velocity'] <= 0.40  # Poor
        assert features['employment_consistency'] <= 0.45  # Declining
    
    def test_demo_profile_partial_data(self):
        """Test DEMO-PARTIAL-001 profile characteristics"""
        fixture_path = 'backend/fixtures/demo_profiles.json'
        
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        # Find DEMO-PARTIAL-001
        partial_profile = next(p for p in data['profiles'] if p['msme_id'] == 'DEMO-PARTIAL-001')
        
        assert partial_profile['sector'] == 'Trader'
        assert partial_profile['expected_risk_band'] == 'Low'
        assert 'missing_sources' in partial_profile
        assert 'EPFO' in partial_profile['missing_sources']
        assert 'adapter_instructions' in partial_profile
