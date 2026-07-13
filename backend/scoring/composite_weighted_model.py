"""
Composite Weighted Scoring Model
Computes financial health scores using sector-specific weighted aggregation
"""
from typing import Dict, List, Optional
from dataclasses import dataclass

from scoring.feature_engineering import NormalizedFeatures


# Valid MSME sectors
VALID_SECTORS = ['Trader', 'Manufacturer', 'Services']


@dataclass
class SectorWeights:
    """Weight configuration for a specific sector"""
    revenue_stability: float
    transaction_velocity: float
    liquidity_ratio: float
    employment_consistency: float
    compliance_score: float
    growth_indicator: float
    
    def to_dict(self) -> Dict[str, float]:
        """Converts SectorWeights to dictionary"""
        return {
            'revenue_stability': self.revenue_stability,
            'transaction_velocity': self.transaction_velocity,
            'liquidity_ratio': self.liquidity_ratio,
            'employment_consistency': self.employment_consistency,
            'compliance_score': self.compliance_score,
            'growth_indicator': self.growth_indicator
        }
    
    def validate(self) -> bool:
        """Validates that weights are non-negative and sum to 1.0"""
        weights_list = [
            self.revenue_stability,
            self.transaction_velocity,
            self.liquidity_ratio,
            self.employment_consistency,
            self.compliance_score,
            self.growth_indicator
        ]
        
        # Check all weights are non-negative
        if any(w < 0 for w in weights_list):
            return False
        
        # Check weights sum to 1.0 (with small tolerance for floating point errors)
        weight_sum = sum(weights_list)
        return abs(weight_sum - 1.0) < 0.0001


class CompositeWeightedModel:
    """
    Computes financial health scores using sector-specific weighted aggregation.
    
    The model applies different feature weights based on the MSME's business sector
    (Trader, Manufacturer, Services) to reflect the varying importance of financial
    health dimensions across business types.
    
    Note: compliance_score and growth_indicator have 0.0 weights because they are
    conceptually incorporated into revenue_stability and transaction_velocity
    to avoid double-counting.
    """
    
    def __init__(self):
        """Initialize composite weighted model with default sector configurations"""
        self._sector_weights = self._load_default_weights()
    
    def _load_default_weights(self) -> Dict[str, SectorWeights]:
        """
        Loads default sector-specific weight configurations.
        
        Returns:
            Dictionary mapping sector names to SectorWeights objects
        """
        return {
            'Trader': SectorWeights(
                revenue_stability=0.25,
                transaction_velocity=0.35,
                liquidity_ratio=0.30,
                employment_consistency=0.10,
                compliance_score=0.0,  # Rolled into revenue_stability
                growth_indicator=0.0   # Rolled into transaction_velocity
            ),
            'Manufacturer': SectorWeights(
                revenue_stability=0.35,
                transaction_velocity=0.20,
                liquidity_ratio=0.25,
                employment_consistency=0.20,
                compliance_score=0.0,
                growth_indicator=0.0
            ),
            'Services': SectorWeights(
                revenue_stability=0.30,
                transaction_velocity=0.25,
                liquidity_ratio=0.20,
                employment_consistency=0.25,
                compliance_score=0.0,
                growth_indicator=0.0
            )
        }
    
    def get_sector_weights(self, sector: str) -> SectorWeights:
        """
        Retrieves sector-specific weight configuration.
        
        Args:
            sector: MSME sector ('Trader', 'Manufacturer', or 'Services')
        
        Returns:
            SectorWeights object for the specified sector
        
        Raises:
            ValueError: If sector is not valid
        """
        if sector not in VALID_SECTORS:
            raise ValueError(
                f"Invalid sector: {sector}. Must be one of {VALID_SECTORS}"
            )
        
        return self._sector_weights[sector]
    
    def adjust_weights(
        self, 
        available_features: List[str], 
        weights: SectorWeights
    ) -> SectorWeights:
        """
        Adjusts weights proportionally when features are missing.
        
        When one or more features are unavailable, this method redistributes
        their weights proportionally across the available features to ensure
        weights still sum to 1.0.
        
        Args:
            available_features: List of feature names that are available
            weights: Original SectorWeights configuration
        
        Returns:
            Adjusted SectorWeights with redistributed weights
        
        Example:
            If employment_consistency is missing (weight=0.10) from Trader:
            - Original: rev=0.25, trans=0.35, liq=0.30, emp=0.10
            - Available sum: 0.90
            - Adjusted: rev=0.278, trans=0.389, liq=0.333, emp=0.0
        """
        weights_dict = weights.to_dict()
        
        # Calculate sum of weights for available features
        available_weight_sum = sum(
            weights_dict[feature] for feature in available_features
            if feature in weights_dict
        )
        
        # If no available features or all weights are zero, return uniform weights
        if available_weight_sum == 0:
            uniform_weight = 1.0 / len(available_features) if available_features else 0.0
            return SectorWeights(
                revenue_stability=uniform_weight if 'revenue_stability' in available_features else 0.0,
                transaction_velocity=uniform_weight if 'transaction_velocity' in available_features else 0.0,
                liquidity_ratio=uniform_weight if 'liquidity_ratio' in available_features else 0.0,
                employment_consistency=uniform_weight if 'employment_consistency' in available_features else 0.0,
                compliance_score=uniform_weight if 'compliance_score' in available_features else 0.0,
                growth_indicator=uniform_weight if 'growth_indicator' in available_features else 0.0
            )
        
        # Proportionally redistribute weights
        adjustment_factor = 1.0 / available_weight_sum
        
        adjusted_weights = SectorWeights(
            revenue_stability=(
                weights_dict['revenue_stability'] * adjustment_factor
                if 'revenue_stability' in available_features
                else 0.0
            ),
            transaction_velocity=(
                weights_dict['transaction_velocity'] * adjustment_factor
                if 'transaction_velocity' in available_features
                else 0.0
            ),
            liquidity_ratio=(
                weights_dict['liquidity_ratio'] * adjustment_factor
                if 'liquidity_ratio' in available_features
                else 0.0
            ),
            employment_consistency=(
                weights_dict['employment_consistency'] * adjustment_factor
                if 'employment_consistency' in available_features
                else 0.0
            ),
            compliance_score=(
                weights_dict['compliance_score'] * adjustment_factor
                if 'compliance_score' in available_features
                else 0.0
            ),
            growth_indicator=(
                weights_dict['growth_indicator'] * adjustment_factor
                if 'growth_indicator' in available_features
                else 0.0
            )
        )
        
        return adjusted_weights
    
    def compute_score(
        self, 
        features: NormalizedFeatures, 
        sector: str,
        available_features: Optional[List[str]] = None
    ) -> float:
        """
        Computes weighted composite score for the given features and sector.
        
        The score is calculated as:
        composite_score = 100 * Σ(weight_i * feature_i)
        
        Where:
        - weight_i: sector-specific weight for feature i
        - feature_i: normalized feature value (0-1)
        - Weights are adjusted proportionally if features are missing
        
        Args:
            features: NormalizedFeatures object with 0-1 scaled values
            sector: MSME sector ('Trader', 'Manufacturer', or 'Services')
            available_features: Optional list of available feature names.
                               If None, all features are assumed available.
        
        Returns:
            Composite score in range 0-100
        
        Raises:
            ValueError: If sector is invalid or features are invalid
        """
        # Validate sector
        if sector not in VALID_SECTORS:
            raise ValueError(
                f"Invalid sector: {sector}. Must be one of {VALID_SECTORS}"
            )
        
        # Get sector weights
        weights = self.get_sector_weights(sector)
        
        # Determine available features
        if available_features is None:
            # Assume all features are available
            available_features = [
                'revenue_stability',
                'transaction_velocity',
                'liquidity_ratio',
                'employment_consistency',
                'compliance_score',
                'growth_indicator'
            ]
        
        # Adjust weights if necessary
        if len(available_features) < 6:
            weights = self.adjust_weights(available_features, weights)
        
        # Convert features to dictionary for easier access
        features_dict = {
            'revenue_stability': features.revenue_stability,
            'transaction_velocity': features.transaction_velocity,
            'liquidity_ratio': features.liquidity_ratio,
            'employment_consistency': features.employment_consistency,
            'compliance_score': features.compliance_score,
            'growth_indicator': features.growth_indicator
        }
        
        weights_dict = weights.to_dict()
        
        # Compute weighted sum
        weighted_sum = 0.0
        for feature_name in available_features:
            if feature_name in features_dict and feature_name in weights_dict:
                feature_value = features_dict[feature_name]
                weight = weights_dict[feature_name]
                weighted_sum += weight * feature_value
        
        # Scale to 0-100 range
        composite_score = 100.0 * weighted_sum
        
        # Ensure score is within bounds
        composite_score = max(0.0, min(100.0, composite_score))
        
        return composite_score
