"""
Unit tests for Composite Weighted Model
Tests sector-specific scoring, weight adjustment, and score bounds
"""
import unittest
from scoring.composite_weighted_model import (
    CompositeWeightedModel,
    SectorWeights,
    VALID_SECTORS
)
from scoring.feature_engineering import NormalizedFeatures


class TestSectorWeights(unittest.TestCase):
    """Tests for SectorWeights dataclass"""
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        weights = SectorWeights(
            revenue_stability=0.25,
            transaction_velocity=0.35,
            liquidity_ratio=0.30,
            employment_consistency=0.10,
            compliance_score=0.0,
            growth_indicator=0.0
        )
        
        weights_dict = weights.to_dict()
        
        self.assertEqual(weights_dict['revenue_stability'], 0.25)
        self.assertEqual(weights_dict['transaction_velocity'], 0.35)
        self.assertEqual(weights_dict['liquidity_ratio'], 0.30)
        self.assertEqual(weights_dict['employment_consistency'], 0.10)
        self.assertEqual(weights_dict['compliance_score'], 0.0)
        self.assertEqual(weights_dict['growth_indicator'], 0.0)
    
    def test_validate_valid_weights(self):
        """Test validation of valid weights"""
        weights = SectorWeights(
            revenue_stability=0.25,
            transaction_velocity=0.35,
            liquidity_ratio=0.30,
            employment_consistency=0.10,
            compliance_score=0.0,
            growth_indicator=0.0
        )
        
        self.assertTrue(weights.validate())
    
    def test_validate_negative_weights(self):
        """Test validation rejects negative weights"""
        weights = SectorWeights(
            revenue_stability=-0.25,
            transaction_velocity=0.35,
            liquidity_ratio=0.30,
            employment_consistency=0.10,
            compliance_score=0.0,
            growth_indicator=0.0
        )
        
        self.assertFalse(weights.validate())
    
    def test_validate_weights_not_sum_to_one(self):
        """Test validation rejects weights that don't sum to 1.0"""
        weights = SectorWeights(
            revenue_stability=0.25,
            transaction_velocity=0.35,
            liquidity_ratio=0.30,
            employment_consistency=0.20,  # Sum = 1.10
            compliance_score=0.0,
            growth_indicator=0.0
        )
        
        self.assertFalse(weights.validate())


class TestCompositeWeightedModel(unittest.TestCase):
    """Tests for CompositeWeightedModel class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = CompositeWeightedModel()
        
        # Sample normalized features
        self.sample_features = NormalizedFeatures(
            revenue_stability=0.8,
            transaction_velocity=0.7,
            liquidity_ratio=0.75,
            employment_consistency=0.65,
            compliance_score=0.9,
            growth_indicator=0.6,
            missing_sources=[]
        )
    
    def test_get_sector_weights_trader(self):
        """Test retrieving Trader sector weights"""
        weights = self.model.get_sector_weights('Trader')
        
        self.assertEqual(weights.revenue_stability, 0.25)
        self.assertEqual(weights.transaction_velocity, 0.35)
        self.assertEqual(weights.liquidity_ratio, 0.30)
        self.assertEqual(weights.employment_consistency, 0.10)
        self.assertEqual(weights.compliance_score, 0.0)
        self.assertEqual(weights.growth_indicator, 0.0)
        self.assertTrue(weights.validate())
    
    def test_get_sector_weights_manufacturer(self):
        """Test retrieving Manufacturer sector weights"""
        weights = self.model.get_sector_weights('Manufacturer')
        
        self.assertEqual(weights.revenue_stability, 0.35)
        self.assertEqual(weights.transaction_velocity, 0.20)
        self.assertEqual(weights.liquidity_ratio, 0.25)
        self.assertEqual(weights.employment_consistency, 0.20)
        self.assertEqual(weights.compliance_score, 0.0)
        self.assertEqual(weights.growth_indicator, 0.0)
        self.assertTrue(weights.validate())
    
    def test_get_sector_weights_services(self):
        """Test retrieving Services sector weights"""
        weights = self.model.get_sector_weights('Services')
        
        self.assertEqual(weights.revenue_stability, 0.30)
        self.assertEqual(weights.transaction_velocity, 0.25)
        self.assertEqual(weights.liquidity_ratio, 0.20)
        self.assertEqual(weights.employment_consistency, 0.25)
        self.assertEqual(weights.compliance_score, 0.0)
        self.assertEqual(weights.growth_indicator, 0.0)
        self.assertTrue(weights.validate())
    
    def test_get_sector_weights_invalid_sector(self):
        """Test that invalid sector raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.model.get_sector_weights('InvalidSector')
        
        self.assertIn('Invalid sector', str(context.exception))
    
    def test_compute_score_trader(self):
        """Test score computation for Trader sector"""
        score = self.model.compute_score(self.sample_features, 'Trader')
        
        # Manual calculation:
        # 0.25 * 0.8 + 0.35 * 0.7 + 0.30 * 0.75 + 0.10 * 0.65 = 0.7325
        # 0.7325 * 100 = 73.25
        expected_score = (
            0.25 * 0.8 +
            0.35 * 0.7 +
            0.30 * 0.75 +
            0.10 * 0.65
        ) * 100
        
        self.assertAlmostEqual(score, expected_score, places=2)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_compute_score_manufacturer(self):
        """Test score computation for Manufacturer sector"""
        score = self.model.compute_score(self.sample_features, 'Manufacturer')
        
        # Manual calculation:
        # 0.35 * 0.8 + 0.20 * 0.7 + 0.25 * 0.75 + 0.20 * 0.65 = 0.7475
        # 0.7475 * 100 = 74.75
        expected_score = (
            0.35 * 0.8 +
            0.20 * 0.7 +
            0.25 * 0.75 +
            0.20 * 0.65
        ) * 100
        
        self.assertAlmostEqual(score, expected_score, places=2)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_compute_score_services(self):
        """Test score computation for Services sector"""
        score = self.model.compute_score(self.sample_features, 'Services')
        
        # Manual calculation:
        # 0.30 * 0.8 + 0.25 * 0.7 + 0.20 * 0.75 + 0.25 * 0.65 = 0.7275
        # 0.7275 * 100 = 72.75
        expected_score = (
            0.30 * 0.8 +
            0.25 * 0.7 +
            0.20 * 0.75 +
            0.25 * 0.65
        ) * 100
        
        self.assertAlmostEqual(score, expected_score, places=2)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_compute_score_low_risk_profile(self):
        """Test score for Low risk profile (should be 70-100)"""
        low_risk_features = NormalizedFeatures(
            revenue_stability=0.88,
            transaction_velocity=0.85,
            liquidity_ratio=0.92,
            employment_consistency=0.82,
            compliance_score=0.95,
            growth_indicator=0.78,
            missing_sources=[]
        )
        
        score = self.model.compute_score(low_risk_features, 'Trader')
        
        self.assertGreaterEqual(score, 70.0)
        self.assertLessEqual(score, 100.0)
    
    def test_compute_score_medium_risk_profile(self):
        """Test score for Medium risk profile (should be 40-69)"""
        medium_risk_features = NormalizedFeatures(
            revenue_stability=0.58,
            transaction_velocity=0.52,
            liquidity_ratio=0.48,
            employment_consistency=0.55,
            compliance_score=0.62,
            growth_indicator=0.45,
            missing_sources=[]
        )
        
        score = self.model.compute_score(medium_risk_features, 'Manufacturer')
        
        self.assertGreaterEqual(score, 40.0)
        self.assertLessEqual(score, 69.0)
    
    def test_compute_score_high_risk_profile(self):
        """Test score for High risk profile (should be 0-39)"""
        high_risk_features = NormalizedFeatures(
            revenue_stability=0.22,
            transaction_velocity=0.18,
            liquidity_ratio=0.25,
            employment_consistency=0.30,
            compliance_score=0.35,
            growth_indicator=0.15,
            missing_sources=[]
        )
        
        score = self.model.compute_score(high_risk_features, 'Services')
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 39.0)
    
    def test_compute_score_bounds_minimum(self):
        """Test that score never goes below 0"""
        zero_features = NormalizedFeatures(
            revenue_stability=0.0,
            transaction_velocity=0.0,
            liquidity_ratio=0.0,
            employment_consistency=0.0,
            compliance_score=0.0,
            growth_indicator=0.0,
            missing_sources=[]
        )
        
        score = self.model.compute_score(zero_features, 'Trader')
        
        self.assertEqual(score, 0.0)
    
    def test_compute_score_bounds_maximum(self):
        """Test that score never exceeds 100"""
        perfect_features = NormalizedFeatures(
            revenue_stability=1.0,
            transaction_velocity=1.0,
            liquidity_ratio=1.0,
            employment_consistency=1.0,
            compliance_score=1.0,
            growth_indicator=1.0,
            missing_sources=[]
        )
        
        score = self.model.compute_score(perfect_features, 'Trader')
        
        self.assertAlmostEqual(score, 100.0, places=5)
    
    def test_compute_score_invalid_sector(self):
        """Test that invalid sector raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.model.compute_score(self.sample_features, 'InvalidSector')
        
        self.assertIn('Invalid sector', str(context.exception))
    
    def test_adjust_weights_one_missing_feature(self):
        """Test weight adjustment when one feature is missing"""
        original_weights = self.model.get_sector_weights('Trader')
        available_features = [
            'revenue_stability',
            'transaction_velocity',
            'liquidity_ratio'
            # employment_consistency is missing (weight=0.10)
        ]
        
        adjusted_weights = self.model.adjust_weights(available_features, original_weights)
        
        # Original available weight sum: 0.25 + 0.35 + 0.30 = 0.90
        # Adjustment factor: 1.0 / 0.90 = 1.1111
        # Adjusted weights:
        # revenue_stability: 0.25 * 1.1111 = 0.2778
        # transaction_velocity: 0.35 * 1.1111 = 0.3889
        # liquidity_ratio: 0.30 * 1.1111 = 0.3333
        
        self.assertAlmostEqual(adjusted_weights.revenue_stability, 0.2778, places=3)
        self.assertAlmostEqual(adjusted_weights.transaction_velocity, 0.3889, places=3)
        self.assertAlmostEqual(adjusted_weights.liquidity_ratio, 0.3333, places=3)
        self.assertEqual(adjusted_weights.employment_consistency, 0.0)
        
        # Verify adjusted weights sum to 1.0
        self.assertTrue(adjusted_weights.validate())
    
    def test_adjust_weights_multiple_missing_features(self):
        """Test weight adjustment when multiple features are missing"""
        original_weights = self.model.get_sector_weights('Manufacturer')
        available_features = [
            'revenue_stability',
            'liquidity_ratio'
            # transaction_velocity and employment_consistency are missing
        ]
        
        adjusted_weights = self.model.adjust_weights(available_features, original_weights)
        
        # Original available weight sum: 0.35 + 0.25 = 0.60
        # Adjustment factor: 1.0 / 0.60 = 1.6667
        # Adjusted weights:
        # revenue_stability: 0.35 * 1.6667 = 0.5833
        # liquidity_ratio: 0.25 * 1.6667 = 0.4167
        
        self.assertAlmostEqual(adjusted_weights.revenue_stability, 0.5833, places=3)
        self.assertEqual(adjusted_weights.transaction_velocity, 0.0)
        self.assertAlmostEqual(adjusted_weights.liquidity_ratio, 0.4167, places=3)
        self.assertEqual(adjusted_weights.employment_consistency, 0.0)
        
        # Verify adjusted weights sum to 1.0
        self.assertTrue(adjusted_weights.validate())
    
    def test_compute_score_with_missing_features(self):
        """Test score computation with missing features"""
        features = NormalizedFeatures(
            revenue_stability=0.8,
            transaction_velocity=0.7,
            liquidity_ratio=0.75,
            employment_consistency=0.65,
            compliance_score=0.9,
            growth_indicator=0.6,
            missing_sources=['EPFO']  # Simulating missing EPFO data
        )
        
        available_features = [
            'revenue_stability',
            'transaction_velocity',
            'liquidity_ratio'
            # employment_consistency not available due to missing EPFO
        ]
        
        score = self.model.compute_score(features, 'Trader', available_features)
        
        # Adjusted weights: rev=0.2778, trans=0.3889, liq=0.3333
        # Score: (0.2778*0.8 + 0.3889*0.7 + 0.3333*0.75) * 100 = 74.44
        expected_score = (
            0.2778 * 0.8 +
            0.3889 * 0.7 +
            0.3333 * 0.75
        ) * 100
        
        self.assertAlmostEqual(score, expected_score, places=1)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_adjust_weights_all_zero_weights(self):
        """Test weight adjustment when all available feature weights are zero"""
        # Create weights where available features all have zero weight
        zero_weights = SectorWeights(
            revenue_stability=0.0,
            transaction_velocity=0.0,
            liquidity_ratio=0.5,
            employment_consistency=0.5,
            compliance_score=0.0,
            growth_indicator=0.0
        )
        
        available_features = [
            'revenue_stability',
            'transaction_velocity'
            # Both have zero weight
        ]
        
        adjusted_weights = self.model.adjust_weights(available_features, zero_weights)
        
        # Should distribute uniformly: 1.0 / 2 = 0.5 each
        self.assertEqual(adjusted_weights.revenue_stability, 0.5)
        self.assertEqual(adjusted_weights.transaction_velocity, 0.5)
        self.assertEqual(adjusted_weights.liquidity_ratio, 0.0)
        self.assertEqual(adjusted_weights.employment_consistency, 0.0)


class TestCompositeWeightedModelIntegration(unittest.TestCase):
    """Integration tests for realistic scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = CompositeWeightedModel()
    
    def test_trader_with_high_transaction_velocity(self):
        """Test that Trader score benefits from high transaction velocity"""
        features = NormalizedFeatures(
            revenue_stability=0.6,
            transaction_velocity=0.95,  # Very high
            liquidity_ratio=0.65,
            employment_consistency=0.55,
            compliance_score=0.7,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        trader_score = self.model.compute_score(features, 'Trader')
        manufacturer_score = self.model.compute_score(features, 'Manufacturer')
        
        # Trader should score higher due to higher transaction_velocity weight (0.35 vs 0.20)
        self.assertGreater(trader_score, manufacturer_score)
    
    def test_manufacturer_with_high_revenue_stability(self):
        """Test that Manufacturer score benefits from high revenue stability"""
        features = NormalizedFeatures(
            revenue_stability=0.95,  # Very high
            transaction_velocity=0.55,
            liquidity_ratio=0.65,
            employment_consistency=0.70,
            compliance_score=0.8,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        manufacturer_score = self.model.compute_score(features, 'Manufacturer')
        trader_score = self.model.compute_score(features, 'Trader')
        
        # Manufacturer should score higher due to higher revenue_stability weight (0.35 vs 0.25)
        self.assertGreater(manufacturer_score, trader_score)
    
    def test_services_with_high_employment_consistency(self):
        """Test that Services score benefits from high employment consistency"""
        features = NormalizedFeatures(
            revenue_stability=0.65,
            transaction_velocity=0.60,
            liquidity_ratio=0.55,
            employment_consistency=0.95,  # Very high
            compliance_score=0.75,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        services_score = self.model.compute_score(features, 'Services')
        trader_score = self.model.compute_score(features, 'Trader')
        
        # Services should score higher due to higher employment_consistency weight (0.25 vs 0.10)
        self.assertGreater(services_score, trader_score)


if __name__ == '__main__':
    unittest.main()
