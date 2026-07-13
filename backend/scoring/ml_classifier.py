"""
ML Classifier for Risk Band Classification
Uses scikit-learn Random Forest with SHAP explainability
"""
from typing import Dict, Tuple, Literal, Optional
from dataclasses import dataclass
import pickle
import json
import os
import numpy as np

from scoring.feature_engineering import NormalizedFeatures


RiskBand = Literal['Low', 'Medium', 'High']


@dataclass
class RiskConfidence:
    """Confidence scores for each risk band"""
    low: float
    medium: float
    high: float


@dataclass
class MLPrediction:
    """ML classification result"""
    risk_band: RiskBand
    confidence: RiskConfidence


@dataclass
class ShapValues:
    """SHAP values for feature explanation"""
    revenue_stability: float
    transaction_velocity: float
    liquidity_ratio: float
    employment_consistency: float
    compliance_score: float
    growth_indicator: float
    
    def to_dict(self) -> Dict[str, float]:
        """Converts to dictionary"""
        return {
            'revenue_stability': self.revenue_stability,
            'transaction_velocity': self.transaction_velocity,
            'liquidity_ratio': self.liquidity_ratio,
            'employment_consistency': self.employment_consistency,
            'compliance_score': self.compliance_score,
            'growth_indicator': self.growth_indicator
        }
    
    def get_ranked_features(self) -> list[Tuple[str, float]]:
        """
        Returns features ranked by absolute SHAP contribution.
        
        Returns:
            List of (feature_name, shap_value) tuples sorted by absolute value descending
        """
        features = self.to_dict()
        return sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)


class MLClassifier:
    """
    ML-based risk classifier using Random Forest and SHAP explainability.
    
    The classifier predicts risk bands (Low/Medium/High) based on 6 normalized
    features and provides SHAP values to explain the prediction.
    
    Model artifacts are loaded from the models/ directory:
    - classifier_v1.pkl: Trained Random Forest classifier
    - explainer_v1.pkl: SHAP TreeExplainer
    """
    
    # Feature names in order expected by the model
    FEATURE_NAMES = [
        'revenue_stability',
        'transaction_velocity', 
        'liquidity_ratio',
        'employment_consistency',
        'compliance_score',
        'growth_indicator'
    ]
    
    # Risk band labels
    RISK_BANDS = ['Low', 'Medium', 'High']
    
    def __init__(self, model_dir: str = 'models'):
        """
        Initialize ML classifier.
        
        Args:
            model_dir: Directory containing model artifacts (default: 'models')
        """
        self.model_dir = model_dir
        self.classifier = None
        self.explainer = None
        self._is_loaded = False
    
    def load_model(self, version: str = 'v1') -> None:
        """
        Loads trained classifier and SHAP explainer from disk.
        
        Args:
            version: Model version to load (default: 'v1')
        
        Raises:
            FileNotFoundError: If model files are not found
            Exception: If model loading fails
        """
        classifier_path = os.path.join(self.model_dir, f'classifier_{version}.pkl')
        explainer_path = os.path.join(self.model_dir, f'explainer_{version}.pkl')
        
        # Check if files exist
        if not os.path.exists(classifier_path):
            raise FileNotFoundError(
                f"Classifier model not found: {classifier_path}. "
                f"Run scripts/train_model.py to generate model artifacts."
            )
        
        if not os.path.exists(explainer_path):
            raise FileNotFoundError(
                f"SHAP explainer not found: {explainer_path}. "
                f"Run scripts/train_model.py to generate model artifacts."
            )
        
        try:
            # Load classifier
            with open(classifier_path, 'rb') as f:
                self.classifier = pickle.load(f)
            
            # Load SHAP explainer
            with open(explainer_path, 'rb') as f:
                self.explainer = pickle.load(f)
            
            self._is_loaded = True
            
            print(f"Successfully loaded ML classifier version {version}")
            
        except Exception as e:
            raise Exception(f"Failed to load model artifacts: {str(e)}")
    
    def predict(self, features: NormalizedFeatures) -> MLPrediction:
        """
        Predicts risk band for given features.
        
        Args:
            features: NormalizedFeatures object with 0-1 scaled values
        
        Returns:
            MLPrediction with risk_band and confidence scores
        
        Raises:
            RuntimeError: If model is not loaded
        """
        if not self._is_loaded:
            raise RuntimeError(
                "Model not loaded. Call load_model() before prediction."
            )
        
        # Convert features to numpy array in correct order
        feature_array = self._features_to_array(features)
        
        # Get prediction probabilities
        probabilities = self.classifier.predict_proba(feature_array.reshape(1, -1))[0]
        
        # Get predicted class
        predicted_class = self.classifier.predict(feature_array.reshape(1, -1))[0]
        
        # Map class index to risk band name
        risk_band = self.RISK_BANDS[predicted_class]
        
        # Create confidence object
        confidence = RiskConfidence(
            low=float(probabilities[0]),
            medium=float(probabilities[1]),
            high=float(probabilities[2])
        )
        
        return MLPrediction(
            risk_band=risk_band,
            confidence=confidence
        )
    
    def explain_prediction(self, features: NormalizedFeatures) -> ShapValues:
        """
        Computes SHAP values for explainability.
        
        SHAP (SHapley Additive exPlanations) values explain how each feature
        contributed to the model's prediction. Positive values push the prediction
        toward higher risk, negative values toward lower risk.
        
        Args:
            features: NormalizedFeatures object with 0-1 scaled values
        
        Returns:
            ShapValues object with SHAP value for each feature
        
        Raises:
            RuntimeError: If model/explainer is not loaded
        """
        if not self._is_loaded:
            raise RuntimeError(
                "Model not loaded. Call load_model() before explanation."
            )
        
        # Convert features to numpy array
        feature_array = self._features_to_array(features)
        
        # Compute SHAP values
        shap_values = self.explainer.shap_values(feature_array.reshape(1, -1))
        
        # For multi-class classification, SHAP returns values for each class
        # We use the values for the predicted class
        predicted_class = self.classifier.predict(feature_array.reshape(1, -1))[0]
        
        # Extract SHAP values for predicted class
        if isinstance(shap_values, list):
            # Multi-class case: shap_values is a list of arrays per class
            # Each class has shape (n_samples, n_features)
            class_shap_values = shap_values[predicted_class][0]
        else:
            # Binary case or already in correct format: shap_values is (n_samples, n_features)
            if len(shap_values.shape) == 2:
                class_shap_values = shap_values[0]
            else:
                class_shap_values = shap_values
        
        # Ensure it's a 1D array
        if len(class_shap_values.shape) > 1:
            class_shap_values = class_shap_values.flatten()
        
        # Create ShapValues object
        return ShapValues(
            revenue_stability=float(class_shap_values[0]),
            transaction_velocity=float(class_shap_values[1]),
            liquidity_ratio=float(class_shap_values[2]),
            employment_consistency=float(class_shap_values[3]),
            compliance_score=float(class_shap_values[4]),
            growth_indicator=float(class_shap_values[5])
        )
    
    def _features_to_array(self, features: NormalizedFeatures) -> np.ndarray:
        """
        Converts NormalizedFeatures to numpy array in correct order.
        
        Args:
            features: NormalizedFeatures object
        
        Returns:
            Numpy array with features in model-expected order
        """
        return np.array([
            features.revenue_stability,
            features.transaction_velocity,
            features.liquidity_ratio,
            features.employment_consistency,
            features.compliance_score,
            features.growth_indicator
        ])
