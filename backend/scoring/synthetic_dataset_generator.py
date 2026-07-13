"""
Synthetic Dataset Generator for ML Training
Generates realistic MSME profiles with risk-correlated features
"""
import random
from typing import Dict, List, Tuple, Literal
from dataclasses import dataclass, asdict
import json

from scoring.feature_engineering import NormalizedFeatures


# Valid MSME sectors
MSMESector = Literal['Trader', 'Manufacturer', 'Services']
RiskBand = Literal['Low', 'Medium', 'High']


@dataclass
class SyntheticProfile:
    """A synthetic MSME profile with features and risk classification"""
    msme_id: str
    sector: MSMESector
    features: Dict[str, float]
    risk_band: RiskBand
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary"""
        return asdict(self)


class SyntheticDatasetGenerator:
    """
    Generates synthetic MSME profiles for ML classifier training.
    
    Profiles are generated with realistic feature-target correlations:
    - Low risk: Strong financial health indicators
    - Medium risk: Moderate indicators with some weaknesses
    - High risk: Weak financial health indicators
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize synthetic dataset generator.
        
        Args:
            seed: Random seed for reproducibility (optional)
        """
        if seed is not None:
            random.seed(seed)
    
    def generate_synthetic_profile(
        self, 
        risk_band: RiskBand, 
        sector: MSMESector,
        msme_id: str = None
    ) -> SyntheticProfile:
        """
        Generates a synthetic MSME profile with realistic feature-label correlations.
        
        Args:
            risk_band: Target risk classification (Low/Medium/High)
            sector: MSME business sector (Trader/Manufacturer/Services)
            msme_id: Optional custom MSME ID (auto-generated if None)
        
        Returns:
            SyntheticProfile with risk-correlated features
        """
        # Generate MSME ID if not provided
        if msme_id is None:
            msme_id = f"MSME-{risk_band[:3].upper()}-{random.randint(10000, 99999)}"
        
        # Generate base features based on risk band
        if risk_band == 'Low':
            # Strong financial health indicators
            # High stability, high liquidity, high compliance
            revenue_stability = random.uniform(0.7, 0.95) + random.gauss(0, 0.05)
            transaction_velocity = random.uniform(0.65, 0.9) + random.gauss(0, 0.08)
            liquidity_ratio = random.uniform(0.6, 1.0) + random.gauss(0, 0.1)
            employment_consistency = random.uniform(0.7, 0.95) + random.gauss(0, 0.05)
            compliance_score = random.uniform(0.8, 1.0) + random.gauss(0, 0.03)
            growth_indicator = random.uniform(0.6, 0.9) + random.gauss(0, 0.08)
            
        elif risk_band == 'Medium':
            # Moderate financial health with some weaknesses
            revenue_stability = random.uniform(0.4, 0.7) + random.gauss(0, 0.1)
            transaction_velocity = random.uniform(0.35, 0.65) + random.gauss(0, 0.1)
            liquidity_ratio = random.uniform(0.3, 0.6) + random.gauss(0, 0.12)
            employment_consistency = random.uniform(0.4, 0.7) + random.gauss(0, 0.1)
            compliance_score = random.uniform(0.5, 0.8) + random.gauss(0, 0.08)
            growth_indicator = random.uniform(0.3, 0.6) + random.gauss(0, 0.1)
            
        else:  # High risk
            # Weak financial health indicators
            # Low stability, poor liquidity, weak compliance
            revenue_stability = random.uniform(0.1, 0.45) + random.gauss(0, 0.1)
            transaction_velocity = random.uniform(0.05, 0.4) + random.gauss(0, 0.12)
            liquidity_ratio = random.uniform(0.05, 0.35) + random.gauss(0, 0.1)
            employment_consistency = random.uniform(0.1, 0.45) + random.gauss(0, 0.12)
            compliance_score = random.uniform(0.2, 0.6) + random.gauss(0, 0.1)
            growth_indicator = random.uniform(0.05, 0.4) + random.gauss(0, 0.15)
        
        # Clip to 0-1 range
        features = {
            'revenue_stability': self._clip(revenue_stability, 0, 1),
            'transaction_velocity': self._clip(transaction_velocity, 0, 1),
            'liquidity_ratio': self._clip(liquidity_ratio, 0, 1),
            'employment_consistency': self._clip(employment_consistency, 0, 1),
            'compliance_score': self._clip(compliance_score, 0, 1),
            'growth_indicator': self._clip(growth_indicator, 0, 1)
        }
        
        # Introduce cross-feature correlations
        features = self._add_correlations(features)
        
        return SyntheticProfile(
            msme_id=msme_id,
            sector=sector,
            features=features,
            risk_band=risk_band
        )
    
    def _add_correlations(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Introduces realistic cross-feature correlations.
        
        Correlations implemented:
        - High revenue stability → higher compliance
        - Low liquidity → lower transaction velocity
        - High growth → higher transaction velocity
        
        Args:
            features: Feature dictionary
        
        Returns:
            Modified feature dictionary with correlations
        """
        # High revenue stability often correlates with good compliance
        if features['revenue_stability'] > 0.7:
            features['compliance_score'] = min(1.0, features['compliance_score'] + 0.1)
        
        # Low liquidity often correlates with reduced transactions
        if features['liquidity_ratio'] < 0.3:
            features['transaction_velocity'] *= 0.8
        
        # High growth often indicates increased transaction activity
        if features['growth_indicator'] > 0.7:
            features['transaction_velocity'] = min(1.0, features['transaction_velocity'] * 1.1)
        
        # Ensure all values remain in 0-1 range after correlations
        for key in features:
            features[key] = self._clip(features[key], 0, 1)
        
        return features
    
    def generate_dataset(
        self, 
        size: int = 1000,
        low_pct: float = 0.5,
        medium_pct: float = 0.3,
        high_pct: float = 0.2
    ) -> List[SyntheticProfile]:
        """
        Generates complete synthetic dataset with specified distribution.
        
        Args:
            size: Total number of profiles to generate (default: 1000)
            low_pct: Percentage of Low risk profiles (default: 0.5 = 50%)
            medium_pct: Percentage of Medium risk profiles (default: 0.3 = 30%)
            high_pct: Percentage of High risk profiles (default: 0.2 = 20%)
        
        Returns:
            List of SyntheticProfile objects
        """
        # Validate percentages
        total_pct = low_pct + medium_pct + high_pct
        if abs(total_pct - 1.0) > 0.01:
            raise ValueError(f"Percentages must sum to 1.0, got {total_pct}")
        
        profiles = []
        
        # Calculate counts per risk band
        low_count = int(size * low_pct)
        medium_count = int(size * medium_pct)
        high_count = size - low_count - medium_count  # Ensure exact total
        
        # Distribute evenly across sectors
        sectors: List[MSMESector] = ['Trader', 'Manufacturer', 'Services']
        
        # Generate profiles for each risk band
        for risk_band, count in [('Low', low_count), ('Medium', medium_count), ('High', high_count)]:
            for i in range(count):
                sector = sectors[i % len(sectors)]
                profile = self.generate_synthetic_profile(risk_band, sector)
                profiles.append(profile)
        
        # Shuffle to avoid ordering bias
        random.shuffle(profiles)
        
        return profiles
    
    def export_to_csv(self, profiles: List[SyntheticProfile], filepath: str) -> None:
        """
        Exports profiles to CSV format compatible with scikit-learn.
        
        Args:
            profiles: List of SyntheticProfile objects
            filepath: Output file path (should end with .csv)
        """
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = [
                'msme_id', 'sector', 
                'revenue_stability', 'transaction_velocity', 'liquidity_ratio',
                'employment_consistency', 'compliance_score', 'growth_indicator',
                'risk_band'
            ]
            writer.writerow(header)
            
            # Write data rows
            for profile in profiles:
                row = [
                    profile.msme_id,
                    profile.sector,
                    profile.features['revenue_stability'],
                    profile.features['transaction_velocity'],
                    profile.features['liquidity_ratio'],
                    profile.features['employment_consistency'],
                    profile.features['compliance_score'],
                    profile.features['growth_indicator'],
                    profile.risk_band
                ]
                writer.writerow(row)
    
    def export_to_json(self, profiles: List[SyntheticProfile], filepath: str) -> None:
        """
        Exports profiles to JSON format.
        
        Args:
            profiles: List of SyntheticProfile objects
            filepath: Output file path (should end with .json)
        """
        data = [profile.to_dict() for profile in profiles]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _clip(self, value: float, min_val: float, max_val: float) -> float:
        """
        Clips value to specified range.
        
        Args:
            value: Value to clip
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            Clipped value
        """
        return max(min_val, min(max_val, value))
