"""
Integration Tests for ML Classifier
Tests with real trained model artifacts
"""
import pytest
import os

from scoring.ml_classifier import MLClassifier, MLPrediction, ShapValues
from scoring.feature_engineering import NormalizedFeatures


class TestMLClassifierIntegration:
    """Integration test suite for MLClassifier with real models"""
    
    @pytest.fixture
    def classifier(self):
        """Fixture that loads the trained model"""
        clf = MLClassifier(model_dir='models')
        
        # Check if model artifacts exist
        if not os.path.exists('models/classifier_v1.pkl'):
            pytest.skip("Model artifacts not found. Run scripts/train_model.py first.")
        
        clf.load_model(version='v1')
        return clf
    
    def test_predict_low_risk_profile(self, classifier):
        """Test prediction on a low risk profile"""
        # Strong financial health indicators
        features = NormalizedFeatures(
            revenue_stability=0.85,
            transaction_velocity=0.80,
            liquidity_ratio=0.85,
            employment_consistency=0.82,
            compliance_score=0.90,
            growth_indicator=0.78,
            missing_sources=[]
        )
        
        prediction = classifier.predict(features)
        
        assert isinstance(prediction, MLPrediction)
        assert prediction.risk_band in ['Low', 'Medium', 'High']
        
        # Should predict Low risk for strong indicators
        assert prediction.risk_band == 'Low'
        
        # Confidence scores should sum to approximately 1.0
        total_confidence = (
            prediction.confidence.low +
            prediction.confidence.medium +
            prediction.confidence.high
        )
        assert abs(total_confidence - 1.0) < 0.01
        
        # Low risk should have highest confidence
        assert prediction.confidence.low > prediction.confidence.medium
        assert prediction.confidence.low > prediction.confidence.high
    
    def test_predict_high_risk_profile(self, classifier):
        """Test prediction on a high risk profile"""
        # Weak financial health indicators
        features = NormalizedFeatures(
            revenue_stability=0.25,
            transaction_velocity=0.20,
            liquidity_ratio=0.15,
            employment_consistency=0.22,
            compliance_score=0.35,
            growth_indicator=0.18,
            missing_sources=[]
        )
        
        prediction = classifier.predict(features)
        
        assert isinstance(prediction, MLPrediction)
        
        # Should predict High risk for weak indicators
        assert prediction.risk_band == 'High'
        
        # High risk should have highest confidence
        assert prediction.confidence.high > prediction.confidence.low
        assert prediction.confidence.high > prediction.confidence.medium
    
    def test_predict_medium_risk_profile(self, classifier):
        """Test prediction on a medium risk profile"""
        # Moderate financial health indicators
        features = NormalizedFeatures(
            revenue_stability=0.55,
            transaction_velocity=0.50,
            liquidity_ratio=0.45,
            employment_consistency=0.52,
            compliance_score=0.65,
            growth_indicator=0.48,
            missing_sources=[]
        )
        
        prediction = classifier.predict(features)
        
        assert isinstance(prediction, MLPrediction)
        
        # Should predict Medium risk for moderate indicators
        assert prediction.risk_band == 'Medium'
        
        # Medium risk should have highest confidence
        assert prediction.confidence.medium > prediction.confidence.low or \
               prediction.confidence.medium > prediction.confidence.high
    
    def test_explain_prediction(self, classifier):
        """Test SHAP explanation generation"""
        features = NormalizedFeatures(
            revenue_stability=0.70,
            transaction_velocity=0.60,
            liquidity_ratio=0.65,
            employment_consistency=0.68,
            compliance_score=0.80,
            growth_indicator=0.55,
            missing_sources=[]
        )
        
        shap_values = classifier.explain_prediction(features)
        
        assert isinstance(shap_values, ShapValues)
        
        # All SHAP values should be numeric
        assert isinstance(shap_values.revenue_stability, float)
        assert isinstance(shap_values.transaction_velocity, float)
        assert isinstance(shap_values.liquidity_ratio, float)
        assert isinstance(shap_values.employment_consistency, float)
        assert isinstance(shap_values.compliance_score, float)
        assert isinstance(shap_values.growth_indicator, float)
    
    def test_shap_values_ranking(self, classifier):
        """Test SHAP values are properly ranked"""
        features = NormalizedFeatures(
            revenue_stability=0.70,
            transaction_velocity=0.60,
            liquidity_ratio=0.65,
            employment_consistency=0.68,
            compliance_score=0.80,
            growth_indicator=0.55,
            missing_sources=[]
        )
        
        shap_values = classifier.explain_prediction(features)
        ranked_features = shap_values.get_ranked_features()
        
        # Should return all 6 features
        assert len(ranked_features) == 6
        
        # Each entry should be a tuple of (feature_name, shap_value)
        for feature_name, shap_value in ranked_features:
            assert isinstance(feature_name, str)
            assert isinstance(shap_value, float)
        
        # Features should be sorted by absolute value descending
        abs_values = [abs(shap_val) for _, shap_val in ranked_features]
        assert abs_values == sorted(abs_values, reverse=True)
    
    def test_predict_and_explain_consistency(self, classifier):
        """Test that prediction and explanation work together"""
        features = NormalizedFeatures(
            revenue_stability=0.75,
            transaction_velocity=0.70,
            liquidity_ratio=0.72,
            employment_consistency=0.68,
            compliance_score=0.85,
            growth_indicator=0.65,
            missing_sources=[]
        )
        
        # Get prediction
        prediction = classifier.predict(features)
        
        # Get explanation
        shap_values = classifier.explain_prediction(features)
        
        # Both should succeed
        assert prediction.risk_band in ['Low', 'Medium', 'High']
        assert isinstance(shap_values, ShapValues)
        
        # SHAP values should exist for all features
        shap_dict = shap_values.to_dict()
        assert len(shap_dict) == 6
    
    def test_edge_case_all_zeros(self, classifier):
        """Test prediction with all zero features"""
        features = NormalizedFeatures(
            revenue_stability=0.0,
            transaction_velocity=0.0,
            liquidity_ratio=0.0,
            employment_consistency=0.0,
            compliance_score=0.0,
            growth_indicator=0.0,
            missing_sources=[]
        )
        
        prediction = classifier.predict(features)
        
        # Should handle edge case without crashing
        assert isinstance(prediction, MLPrediction)
        assert prediction.risk_band in ['Low', 'Medium', 'High']
        
        # Most likely High risk
        assert prediction.risk_band == 'High'
    
    def test_edge_case_all_ones(self, classifier):
        """Test prediction with all maximum features"""
        features = NormalizedFeatures(
            revenue_stability=1.0,
            transaction_velocity=1.0,
            liquidity_ratio=1.0,
            employment_consistency=1.0,
            compliance_score=1.0,
            growth_indicator=1.0,
            missing_sources=[]
        )
        
        prediction = classifier.predict(features)
        
        # Should handle edge case without crashing
        assert isinstance(prediction, MLPrediction)
        assert prediction.risk_band in ['Low', 'Medium', 'High']
        
        # Most likely Low risk
        assert prediction.risk_band == 'Low'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
