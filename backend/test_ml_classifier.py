"""
Unit Tests for ML Classifier
Tests prediction, explainability, and model loading
"""
import pytest
import os
import numpy as np
from unittest.mock import Mock, patch, mock_open
import pickle

from scoring.ml_classifier import MLClassifier, MLPrediction, RiskConfidence, ShapValues
from scoring.feature_engineering import NormalizedFeatures


class TestMLClassifier:
    """Test suite for MLClassifier"""
    
    def test_initialization(self):
        """Test MLClassifier initialization"""
        classifier = MLClassifier(model_dir='models')
        
        assert classifier.model_dir == 'models'
        assert classifier.classifier is None
        assert classifier.explainer is None
        assert classifier._is_loaded is False
    
    def test_load_model_file_not_found(self):
        """Test load_model raises error when files don't exist"""
        classifier = MLClassifier(model_dir='nonexistent_dir')
        
        with pytest.raises(FileNotFoundError, match="Classifier model not found"):
            classifier.load_model(version='v1')
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.load')
    def test_load_model_success(self, mock_pickle_load, mock_file, mock_exists):
        """Test successful model loading"""
        # Mock file existence
        mock_exists.return_value = True
        
        # Create mock classifier and explainer
        mock_classifier = Mock()
        mock_explainer = Mock()
        
        # Mock pickle.load to return classifier first, then explainer
        mock_pickle_load.side_effect = [mock_classifier, mock_explainer]
        
        classifier = MLClassifier(model_dir='models')
        classifier.load_model(version='v1')
        
        assert classifier._is_loaded is True
        assert classifier.classifier == mock_classifier
        assert classifier.explainer == mock_explainer
    
    def test_predict_without_loading(self):
        """Test predict raises error when model not loaded"""
        classifier = MLClassifier()
        
        features = NormalizedFeatures(
            revenue_stability=0.7,
            transaction_velocity=0.6,
            liquidity_ratio=0.8,
            employment_consistency=0.65,
            compliance_score=0.85,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            classifier.predict(features)
    
    def test_explain_prediction_without_loading(self):
        """Test explain_prediction raises error when model not loaded"""
        classifier = MLClassifier()
        
        features = NormalizedFeatures(
            revenue_stability=0.7,
            transaction_velocity=0.6,
            liquidity_ratio=0.8,
            employment_consistency=0.65,
            compliance_score=0.85,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            classifier.explain_prediction(features)
    
    def test_predict_with_mock_model(self):
        """Test prediction with mocked model"""
        classifier = MLClassifier()
        
        # Create mock classifier
        mock_classifier = Mock()
        mock_classifier.predict.return_value = np.array([0])  # Low risk
        mock_classifier.predict_proba.return_value = np.array([[0.8, 0.15, 0.05]])
        
        classifier.classifier = mock_classifier
        classifier._is_loaded = True
        
        features = NormalizedFeatures(
            revenue_stability=0.7,
            transaction_velocity=0.6,
            liquidity_ratio=0.8,
            employment_consistency=0.65,
            compliance_score=0.85,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        prediction = classifier.predict(features)
        
        assert isinstance(prediction, MLPrediction)
        assert prediction.risk_band == 'Low'
        assert prediction.confidence.low == 0.8
        assert prediction.confidence.medium == 0.15
        assert prediction.confidence.high == 0.05
    
    def test_explain_prediction_with_mock_model(self):
        """Test SHAP explanation with mocked model"""
        classifier = MLClassifier()
        
        # Create mock classifier and explainer
        mock_classifier = Mock()
        mock_classifier.predict.return_value = np.array([1])  # Medium risk
        
        mock_explainer = Mock()
        # SHAP values for multi-class (list of arrays per class)
        mock_explainer.shap_values.return_value = [
            np.array([[0.1, 0.2, 0.15, 0.05, 0.1, 0.08]]),  # Low class
            np.array([[0.12, -0.08, 0.15, 0.03, 0.09, -0.05]]),  # Medium class
            np.array([[-0.05, -0.1, -0.08, -0.02, -0.06, -0.03]])  # High class
        ]
        
        classifier.classifier = mock_classifier
        classifier.explainer = mock_explainer
        classifier._is_loaded = True
        
        features = NormalizedFeatures(
            revenue_stability=0.7,
            transaction_velocity=0.6,
            liquidity_ratio=0.8,
            employment_consistency=0.65,
            compliance_score=0.85,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        shap_values = classifier.explain_prediction(features)
        
        assert isinstance(shap_values, ShapValues)
        assert shap_values.revenue_stability == 0.12
        assert shap_values.transaction_velocity == -0.08
        assert shap_values.liquidity_ratio == 0.15
        assert shap_values.employment_consistency == 0.03
        assert shap_values.compliance_score == 0.09
        assert shap_values.growth_indicator == -0.05
    
    def test_shap_values_to_dict(self):
        """Test ShapValues to_dict method"""
        shap_values = ShapValues(
            revenue_stability=0.12,
            transaction_velocity=-0.08,
            liquidity_ratio=0.15,
            employment_consistency=0.03,
            compliance_score=0.09,
            growth_indicator=-0.05
        )
        
        result = shap_values.to_dict()
        
        assert isinstance(result, dict)
        assert result['revenue_stability'] == 0.12
        assert result['transaction_velocity'] == -0.08
        assert result['liquidity_ratio'] == 0.15
        assert result['employment_consistency'] == 0.03
        assert result['compliance_score'] == 0.09
        assert result['growth_indicator'] == -0.05
    
    def test_shap_values_get_ranked_features(self):
        """Test ShapValues feature ranking by absolute contribution"""
        shap_values = ShapValues(
            revenue_stability=0.12,
            transaction_velocity=-0.08,
            liquidity_ratio=0.15,
            employment_consistency=0.03,
            compliance_score=0.09,
            growth_indicator=-0.05
        )
        
        ranked = shap_values.get_ranked_features()
        
        assert isinstance(ranked, list)
        assert len(ranked) == 6
        
        # Check ranking order (by absolute value)
        assert ranked[0] == ('liquidity_ratio', 0.15)
        assert ranked[1] == ('revenue_stability', 0.12)
        assert ranked[2] == ('compliance_score', 0.09)
        assert ranked[3] == ('transaction_velocity', -0.08)
        assert ranked[4] == ('growth_indicator', -0.05)
        assert ranked[5] == ('employment_consistency', 0.03)
    
    def test_features_to_array(self):
        """Test feature conversion to numpy array"""
        classifier = MLClassifier()
        
        features = NormalizedFeatures(
            revenue_stability=0.7,
            transaction_velocity=0.6,
            liquidity_ratio=0.8,
            employment_consistency=0.65,
            compliance_score=0.85,
            growth_indicator=0.6,
            missing_sources=[]
        )
        
        array = classifier._features_to_array(features)
        
        assert isinstance(array, np.ndarray)
        assert array.shape == (6,)
        assert array[0] == 0.7  # revenue_stability
        assert array[1] == 0.6  # transaction_velocity
        assert array[2] == 0.8  # liquidity_ratio
        assert array[3] == 0.65  # employment_consistency
        assert array[4] == 0.85  # compliance_score
        assert array[5] == 0.6  # growth_indicator
    
    def test_risk_confidence_dataclass(self):
        """Test RiskConfidence dataclass"""
        confidence = RiskConfidence(low=0.7, medium=0.2, high=0.1)
        
        assert confidence.low == 0.7
        assert confidence.medium == 0.2
        assert confidence.high == 0.1
    
    def test_ml_prediction_dataclass(self):
        """Test MLPrediction dataclass"""
        confidence = RiskConfidence(low=0.7, medium=0.2, high=0.1)
        prediction = MLPrediction(risk_band='Low', confidence=confidence)
        
        assert prediction.risk_band == 'Low'
        assert prediction.confidence == confidence


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
