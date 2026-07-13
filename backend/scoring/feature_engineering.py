"""
Feature Engineering Pipeline
Transforms raw data from adapters into normalized features for scoring
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import statistics

from adapters.base_adapter import NormalizedData


@dataclass
class EngineeredFeatures:
    """Raw engineered features (unnormalized)"""
    revenue_stability: float
    transaction_velocity: float
    liquidity_ratio: float
    employment_consistency: float
    compliance_score: float
    growth_indicator: float
    
    # Metadata for tracking
    missing_sources: List[str]


@dataclass
class NormalizedFeatures:
    """Normalized features (0-1 scale)"""
    revenue_stability: float  # 0-1
    transaction_velocity: float  # 0-1
    liquidity_ratio: float  # 0-1
    employment_consistency: float  # 0-1
    compliance_score: float  # 0-1
    growth_indicator: float  # 0-1
    
    # Metadata for tracking
    missing_sources: List[str]


class FeatureEngineeringPipeline:
    """
    Transforms raw data from all adapters into scoring features.
    Handles missing data with imputation and normalizes features to 0-1 scale.
    """
    
    def __init__(self):
        """Initialize feature engineering pipeline"""
        # Default imputation values for missing features
        self._default_imputation = {
            'revenue_stability': 0.5,
            'transaction_velocity': 0.3,
            'liquidity_ratio': 0.4,
            'employment_consistency': 0.5,
            'compliance_score': 0.6,
            'growth_indicator': 0.5
        }
    
    def compute_features(self, data_map: Dict[str, NormalizedData]) -> EngineeredFeatures:
        """
        Transforms raw data from all adapters into scoring features.
        
        Args:
            data_map: Dictionary mapping source names to NormalizedData objects
                     Keys: 'GST', 'UPI', 'AA', 'EPFO'
        
        Returns:
            EngineeredFeatures object with computed features
        """
        missing_sources = []
        
        # Extract data from each source
        gst_data = data_map.get('GST')
        upi_data = data_map.get('UPI')
        aa_data = data_map.get('AA')
        epfo_data = data_map.get('EPFO')
        
        # Track missing sources
        if not gst_data:
            missing_sources.append('GST')
        if not upi_data:
            missing_sources.append('UPI')
        if not aa_data:
            missing_sources.append('AA')
        if not epfo_data:
            missing_sources.append('EPFO')
        
        # Compute individual features
        revenue_stability = self._compute_revenue_stability(gst_data)
        transaction_velocity = self._compute_transaction_velocity(upi_data)
        liquidity_ratio = self._compute_liquidity_ratio(aa_data)
        employment_consistency = self._compute_employment_consistency(epfo_data)
        compliance_score = self._compute_compliance_score(gst_data)
        growth_indicator = self._compute_growth_indicator(gst_data, upi_data, epfo_data)
        
        return EngineeredFeatures(
            revenue_stability=revenue_stability,
            transaction_velocity=transaction_velocity,
            liquidity_ratio=liquidity_ratio,
            employment_consistency=employment_consistency,
            compliance_score=compliance_score,
            growth_indicator=growth_indicator,
            missing_sources=missing_sources
        )
    
    def impute_missing_features(self, features: EngineeredFeatures) -> EngineeredFeatures:
        """
        Applies imputation strategy for missing data.
        
        Args:
            features: EngineeredFeatures object with potentially missing values
        
        Returns:
            EngineeredFeatures object with imputed values
        """
        # If a feature is None or negative (indicating missing), use default imputation
        return EngineeredFeatures(
            revenue_stability=features.revenue_stability if features.revenue_stability is not None and features.revenue_stability >= 0 
                            else self._default_imputation['revenue_stability'],
            transaction_velocity=features.transaction_velocity if features.transaction_velocity is not None and features.transaction_velocity >= 0 
                                else self._default_imputation['transaction_velocity'],
            liquidity_ratio=features.liquidity_ratio if features.liquidity_ratio is not None and features.liquidity_ratio >= 0 
                          else self._default_imputation['liquidity_ratio'],
            employment_consistency=features.employment_consistency if features.employment_consistency is not None and features.employment_consistency >= 0 
                                 else self._default_imputation['employment_consistency'],
            compliance_score=features.compliance_score if features.compliance_score is not None and features.compliance_score >= 0 
                           else self._default_imputation['compliance_score'],
            growth_indicator=features.growth_indicator if features.growth_indicator is not None and features.growth_indicator >= 0 
                           else self._default_imputation['growth_indicator'],
            missing_sources=features.missing_sources
        )
    
    def normalize_features(self, features: EngineeredFeatures) -> NormalizedFeatures:
        """
        Normalizes features to 0-1 scale using min-max normalization.
        
        Args:
            features: EngineeredFeatures object with raw values
        
        Returns:
            NormalizedFeatures object with 0-1 scaled values
        """
        # Most features are already in 0-1 range from computation, but ensure bounds
        def clip(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
            """Clip value to specified range"""
            return max(min_val, min(max_val, value))
        
        return NormalizedFeatures(
            revenue_stability=clip(features.revenue_stability),
            transaction_velocity=clip(features.transaction_velocity),
            liquidity_ratio=clip(features.liquidity_ratio),
            employment_consistency=clip(features.employment_consistency),
            compliance_score=clip(features.compliance_score),
            growth_indicator=clip(features.growth_indicator),
            missing_sources=features.missing_sources
        )
    
    # Feature computation methods
    
    def _compute_revenue_stability(self, gst_data: Optional[NormalizedData]) -> Optional[float]:
        """
        Computes revenue stability using coefficient of variation.
        Formula: revenue_stability = 1 - (std_dev(monthly_revenue) / mean(monthly_revenue))
        
        Args:
            gst_data: Normalized GST data
        
        Returns:
            Revenue stability score (0-1), or None if data unavailable
        """
        if not gst_data:
            return None
        
        # We need monthly revenue data to calculate stability
        # Since normalized data doesn't include monthly breakdown, we'll use
        # revenue growth rate as a proxy for stability
        # Higher growth rate variance = lower stability
        
        revenue_growth_rate = gst_data.data.get('revenue_growth_rate', 0)
        
        # Convert growth rate to stability metric
        # Stable businesses have growth rates between -10% and +20%
        # Map this to 0-1 scale
        if abs(revenue_growth_rate) <= 10:
            # Very stable
            stability = 0.8 + (10 - abs(revenue_growth_rate)) / 100
        elif abs(revenue_growth_rate) <= 30:
            # Moderately stable
            stability = 0.6 - (abs(revenue_growth_rate) - 10) / 100
        else:
            # Less stable
            stability = max(0.3, 0.6 - (abs(revenue_growth_rate) - 30) / 200)
        
        return min(1.0, max(0.0, stability))
    
    def _compute_transaction_velocity(self, upi_data: Optional[NormalizedData]) -> Optional[float]:
        """
        Computes transaction velocity composite metric.
        Formula: transaction_velocity = 0.6 * normalize(volume) + 0.4 * normalize(frequency)
        
        Args:
            upi_data: Normalized UPI data
        
        Returns:
            Transaction velocity score (0-1), or None if data unavailable
        """
        if not upi_data:
            return None
        
        monthly_volume = upi_data.data.get('monthly_transaction_volume', 0)
        transaction_frequency = upi_data.data.get('transaction_frequency', 0)
        
        # Normalize volume (assume healthy MSME does 1M-50M monthly)
        volume_normalized = self._normalize_value(monthly_volume, 1_000_000, 50_000_000)
        
        # Normalize frequency (assume healthy MSME does 100-800 transactions/month)
        frequency_normalized = self._normalize_value(transaction_frequency, 100, 800)
        
        # Weighted composite
        velocity = 0.6 * volume_normalized + 0.4 * frequency_normalized
        
        return min(1.0, max(0.0, velocity))
    
    def _compute_liquidity_ratio(self, aa_data: Optional[NormalizedData]) -> Optional[float]:
        """
        Computes liquidity ratio.
        Formula: liquidity_ratio = min(1.0, current_balance / average_monthly_outflow)
        
        Args:
            aa_data: Normalized Account Aggregator data
        
        Returns:
            Liquidity ratio score (0-1), or None if data unavailable
        """
        if not aa_data:
            return None
        
        # Directly use the liquidity ratio from AA adapter (already computed)
        liquidity_ratio = aa_data.data.get('liquidity_ratio', 0)
        
        # Cap at 1.0 (100% liquidity coverage)
        return min(1.0, max(0.0, liquidity_ratio))
    
    def _compute_employment_consistency(self, epfo_data: Optional[NormalizedData]) -> Optional[float]:
        """
        Computes employment consistency composite metric.
        Formula: employment_consistency = 
            0.5 * contribution_regularity + 
            0.3 * (1 - employee_churn_rate) +
            0.2 * normalize(employee_count)
        
        Args:
            epfo_data: Normalized EPFO data
        
        Returns:
            Employment consistency score (0-1), or None if data unavailable
        """
        if not epfo_data:
            return None
        
        contribution_regularity = epfo_data.data.get('contribution_regularity', 0)
        employee_growth_rate = epfo_data.data.get('employee_growth_rate', 0)
        employee_count = epfo_data.data.get('employee_count', 0)
        
        # Convert growth rate to churn proxy (high volatility = high churn)
        # Stable growth (-5% to +15%) is good, extreme changes indicate churn
        if abs(employee_growth_rate) <= 15:
            churn_factor = 1.0 - (abs(employee_growth_rate) / 100)
        else:
            churn_factor = max(0.3, 0.85 - (abs(employee_growth_rate) - 15) / 100)
        
        # Normalize employee count (5-100 for MSMEs)
        employee_count_normalized = self._normalize_value(employee_count, 5, 100)
        
        # Weighted composite
        consistency = (
            0.5 * contribution_regularity +
            0.3 * churn_factor +
            0.2 * employee_count_normalized
        )
        
        return min(1.0, max(0.0, consistency))
    
    def _compute_compliance_score(self, gst_data: Optional[NormalizedData]) -> Optional[float]:
        """
        Computes compliance score.
        Formula: compliance_score = filing_frequency * compliance_status_multiplier
        
        Args:
            gst_data: Normalized GST data
        
        Returns:
            Compliance score (0-1), or None if data unavailable
        """
        if not gst_data:
            return None
        
        filing_frequency = gst_data.data.get('filing_frequency', 0)
        compliance_status = gst_data.data.get('compliance_status', 'non-compliant')
        
        # Determine compliance status multiplier
        status_multiplier = {
            'compliant': 1.0,
            'partial': 0.7,
            'non-compliant': 0.3
        }.get(compliance_status, 0.5)
        
        compliance_score = filing_frequency * status_multiplier
        
        return min(1.0, max(0.0, compliance_score))
    
    def _compute_growth_indicator(
        self, 
        gst_data: Optional[NormalizedData],
        upi_data: Optional[NormalizedData],
        epfo_data: Optional[NormalizedData]
    ) -> Optional[float]:
        """
        Computes growth indicator composite metric.
        Formula: growth_indicator = normalize(
            0.4 * revenue_growth_rate +
            0.3 * transaction_growth_rate +
            0.3 * employee_growth_rate
        )
        
        Args:
            gst_data: Normalized GST data
            upi_data: Normalized UPI data
            epfo_data: Normalized EPFO data
        
        Returns:
            Growth indicator score (0-1), or None if all data unavailable
        """
        # Collect available growth rates
        growth_rates = []
        weights = []
        
        if gst_data:
            revenue_growth_rate = gst_data.data.get('revenue_growth_rate', 0)
            growth_rates.append(revenue_growth_rate)
            weights.append(0.4)
        
        if upi_data:
            transaction_growth_rate = upi_data.data.get('transaction_growth_rate', 0)
            growth_rates.append(transaction_growth_rate)
            weights.append(0.3)
        
        if epfo_data:
            employee_growth_rate = epfo_data.data.get('employee_growth_rate', 0)
            growth_rates.append(employee_growth_rate)
            weights.append(0.3)
        
        if not growth_rates:
            return None
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Weighted average of growth rates
        weighted_growth = sum(rate * weight for rate, weight in zip(growth_rates, normalized_weights))
        
        # Transform growth rate to 0-1 scale using sigmoid-like transformation
        # Healthy growth: 0-30% maps to 0.5-0.9
        # Negative growth: -20-0% maps to 0.1-0.5
        if weighted_growth >= 0:
            # Positive growth
            normalized_growth = 0.5 + (min(weighted_growth, 30) / 30) * 0.4
        else:
            # Negative growth
            normalized_growth = 0.5 + (max(weighted_growth, -20) / 20) * 0.4
        
        return min(1.0, max(0.0, normalized_growth))
    
    def _normalize_value(self, value: float, min_expected: float, max_expected: float) -> float:
        """
        Normalizes a value to 0-1 scale using min-max normalization.
        
        Args:
            value: Value to normalize
            min_expected: Expected minimum value
            max_expected: Expected maximum value
        
        Returns:
            Normalized value (0-1)
        """
        if max_expected == min_expected:
            return 0.5
        
        normalized = (value - min_expected) / (max_expected - min_expected)
        return min(1.0, max(0.0, normalized))
