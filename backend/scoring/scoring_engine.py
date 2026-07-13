"""
Scoring Engine Orchestration
Orchestrates data retrieval, feature engineering, and score computation
"""
from typing import Dict, Optional, List, Literal
from dataclasses import dataclass
from datetime import datetime

from adapters.gst_adapter import GSTAdapter
from adapters.upi_adapter import UPIAdapter
from adapters.aa_adapter import AAAdapter
from adapters.epfo_adapter import EPFOAdapter
from adapters.base_adapter import NormalizedData
from scoring.feature_engineering import FeatureEngineeringPipeline, NormalizedFeatures
from scoring.composite_weighted_model import CompositeWeightedModel
from scoring.ml_classifier import MLClassifier, RiskBand, RiskConfidence, ShapValues


@dataclass
class MSMEIdentifiers:
    """MSME identification data for all adapters"""
    msme_id: str
    gst_number: str
    upi_id: str
    aa_consent_token: str
    epfo_establishment_id: str
    sector: Literal['Trader', 'Manufacturer', 'Services']


@dataclass
class ScoreResult:
    """Complete score computation result"""
    msme_id: str
    composite_score: float  # 0-100
    ml_risk_band: RiskBand
    ml_confidence: RiskConfidence
    shap_values: ShapValues
    features: NormalizedFeatures
    missing_data_sources: List[str]
    computed_at: datetime
    sector: str


class ScoringEngine:
    """
    Orchestrates the complete scoring workflow:
    1. Data retrieval from all adapters
    2. Feature engineering
    3. Composite score computation
    4. ML risk classification
    5. SHAP explainability
    
    Handles partial data scenarios gracefully with missing source tracking.
    """
    
    def __init__(self, mode: Literal['mock', 'production'] = 'mock', model_dir: str = 'models'):
        """
        Initialize scoring engine with all components.
        
        Args:
            mode: Adapter mode ('mock' or 'production')
            model_dir: Directory containing ML model artifacts
        """
        # Initialize adapters
        self.gst_adapter = GSTAdapter()
        self.upi_adapter = UPIAdapter()
        self.aa_adapter = AAAdapter()
        self.epfo_adapter = EPFOAdapter()
        
        # Set adapter mode
        for adapter in [self.gst_adapter, self.upi_adapter, self.aa_adapter, self.epfo_adapter]:
            adapter.set_mode(mode)
        
        # Initialize scoring components
        self.feature_pipeline = FeatureEngineeringPipeline()
        self.composite_model = CompositeWeightedModel()
        self.ml_classifier = MLClassifier(model_dir=model_dir)
        
        # Load ML model
        try:
            self.ml_classifier.load_model()
        except Exception as e:
            print(f"Warning: Failed to load ML model: {e}")
            print("ML classification will be unavailable until model is trained.")
    
    def gather_data(self, identifiers: MSMEIdentifiers) -> Dict[str, NormalizedData]:
        """
        Orchestrates data retrieval from all adapters.
        
        Calls each adapter and collects normalized data. If an adapter fails,
        continues with remaining adapters and tracks the failure.
        
        Args:
            identifiers: MSME identification data for all adapters
        
        Returns:
            Dictionary mapping source names ('GST', 'UPI', 'AA', 'EPFO') to
            NormalizedData objects. Missing sources are not included.
        """
        data_map: Dict[str, NormalizedData] = {}
        
        # Attempt GST data retrieval
        try:
            gst_raw = self.gst_adapter.fetch_data(identifiers.gst_number)
            gst_normalized = self.gst_adapter.normalize_data(gst_raw)
            data_map['GST'] = gst_normalized
        except Exception as e:
            print(f"GST adapter failed: {e}")
        
        # Attempt UPI data retrieval
        try:
            upi_raw = self.upi_adapter.fetch_data(identifiers.upi_id)
            upi_normalized = self.upi_adapter.normalize_data(upi_raw)
            data_map['UPI'] = upi_normalized
        except Exception as e:
            print(f"UPI adapter failed: {e}")
        
        # Attempt AA data retrieval
        try:
            aa_raw = self.aa_adapter.fetch_data(identifiers.aa_consent_token)
            aa_normalized = self.aa_adapter.normalize_data(aa_raw)
            data_map['AA'] = aa_normalized
        except Exception as e:
            print(f"AA adapter failed: {e}")
        
        # Attempt EPFO data retrieval
        try:
            epfo_raw = self.epfo_adapter.fetch_data(identifiers.epfo_establishment_id)
            epfo_normalized = self.epfo_adapter.normalize_data(epfo_raw)
            data_map['EPFO'] = epfo_normalized
        except Exception as e:
            print(f"EPFO adapter failed: {e}")
        
        return data_map
    
    def compute_score(self, identifiers: MSMEIdentifiers) -> ScoreResult:
        """
        Computes comprehensive financial health score.
        
        Orchestrates the complete workflow:
        1. Gather data from all adapters
        2. Engineer features with imputation for missing data
        3. Compute composite weighted score
        4. Predict risk band with ML classifier
        5. Generate SHAP explainability values
        
        Args:
            identifiers: MSME identification data
        
        Returns:
            ScoreResult with complete scoring information
        
        Raises:
            ValueError: If no data sources are available
            RuntimeError: If ML model is not loaded
        """
        # Step 1: Gather data from all adapters
        data_map = self.gather_data(identifiers)
        
        # Check if we have any data
        if not data_map:
            raise ValueError(
                "No data sources available. All adapters failed. "
                "Cannot compute score without any data."
            )
        
        # Step 2: Engineer features
        engineered_features = self.feature_pipeline.compute_features(data_map)
        
        # Step 3: Impute missing features
        imputed_features = self.feature_pipeline.impute_missing_features(engineered_features)
        
        # Step 4: Normalize features
        normalized_features = self.feature_pipeline.normalize_features(imputed_features)
        
        # Determine available features for weight adjustment
        available_feature_names = [
            name for name in [
                'revenue_stability', 'transaction_velocity', 'liquidity_ratio',
                'employment_consistency', 'compliance_score', 'growth_indicator'
            ]
            if name not in [
                f.lower().replace(' ', '_')
                for f in normalized_features.missing_sources
            ]
        ]
        
        # Step 5: Compute composite score
        composite_score = self.composite_model.compute_score(
            features=normalized_features,
            sector=identifiers.sector,
            available_features=available_feature_names if len(normalized_features.missing_sources) > 0 else None
        )
        
        # Step 6: ML risk classification
        ml_prediction = self.ml_classifier.predict(normalized_features)
        
        # Step 7: SHAP explainability
        shap_values = self.ml_classifier.explain_prediction(normalized_features)
        
        # Step 8: Assemble result
        return ScoreResult(
            msme_id=identifiers.msme_id,
            composite_score=composite_score,
            ml_risk_band=ml_prediction.risk_band,
            ml_confidence=ml_prediction.confidence,
            shap_values=shap_values,
            features=normalized_features,
            missing_data_sources=normalized_features.missing_sources,
            computed_at=datetime.now(),
            sector=identifiers.sector
        )
    
    def compute_with_partial_data(
        self,
        features: NormalizedFeatures,
        sector: Literal['Trader', 'Manufacturer', 'Services']
    ) -> ScoreResult:
        """
        Computes score using pre-computed features (for what-if simulation).
        
        This method bypasses data gathering and feature engineering, allowing
        for fast score recalculation with adjusted feature values. Used by
        the what-if simulator for real-time scoring.
        
        Args:
            features: Pre-computed normalized features
            sector: MSME sector
        
        Returns:
            ScoreResult with scoring information
        
        Raises:
            RuntimeError: If ML model is not loaded
        """
        # Determine available features
        available_feature_names = [
            name for name in [
                'revenue_stability', 'transaction_velocity', 'liquidity_ratio',
                'employment_consistency', 'compliance_score', 'growth_indicator'
            ]
            if name not in [
                f.lower().replace(' ', '_')
                for f in features.missing_sources
            ]
        ]
        
        # Compute composite score
        composite_score = self.composite_model.compute_score(
            features=features,
            sector=sector,
            available_features=available_feature_names if len(features.missing_sources) > 0 else None
        )
        
        # ML risk classification
        ml_prediction = self.ml_classifier.predict(features)
        
        # SHAP explainability
        shap_values = self.ml_classifier.explain_prediction(features)
        
        # Assemble result
        return ScoreResult(
            msme_id="simulation",
            composite_score=composite_score,
            ml_risk_band=ml_prediction.risk_band,
            ml_confidence=ml_prediction.confidence,
            shap_values=shap_values,
            features=features,
            missing_data_sources=features.missing_sources,
            computed_at=datetime.now(),
            sector=sector
        )
