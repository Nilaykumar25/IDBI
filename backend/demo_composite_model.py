"""
Demonstration script for CompositeWeightedModel
Shows scoring behavior across different sectors and risk profiles
"""
from scoring.composite_weighted_model import CompositeWeightedModel
from scoring.feature_engineering import NormalizedFeatures


def main():
    """Demonstrates composite weighted model functionality"""
    model = CompositeWeightedModel()
    
    print("=" * 70)
    print("MSME Financial Health Score - Composite Weighted Model Demo")
    print("=" * 70)
    print()
    
    # Demo 1: Low Risk Profile
    print("Demo 1: Low Risk Profile (Trader)")
    print("-" * 70)
    low_risk = NormalizedFeatures(
        revenue_stability=0.88,
        transaction_velocity=0.85,
        liquidity_ratio=0.92,
        employment_consistency=0.82,
        compliance_score=0.95,
        growth_indicator=0.78,
        missing_sources=[]
    )
    
    score = model.compute_score(low_risk, 'Trader')
    print(f"Features: Revenue={low_risk.revenue_stability:.2f}, "
          f"Transaction={low_risk.transaction_velocity:.2f}, "
          f"Liquidity={low_risk.liquidity_ratio:.2f}, "
          f"Employment={low_risk.employment_consistency:.2f}")
    print(f"Score: {score:.2f} (Expected: 70-100 for Low Risk)")
    print()
    
    # Demo 2: High Risk Profile
    print("Demo 2: High Risk Profile (Services)")
    print("-" * 70)
    high_risk = NormalizedFeatures(
        revenue_stability=0.22,
        transaction_velocity=0.18,
        liquidity_ratio=0.25,
        employment_consistency=0.30,
        compliance_score=0.35,
        growth_indicator=0.15,
        missing_sources=[]
    )
    
    score = model.compute_score(high_risk, 'Services')
    print(f"Features: Revenue={high_risk.revenue_stability:.2f}, "
          f"Transaction={high_risk.transaction_velocity:.2f}, "
          f"Liquidity={high_risk.liquidity_ratio:.2f}, "
          f"Employment={high_risk.employment_consistency:.2f}")
    print(f"Score: {score:.2f} (Expected: 0-39 for High Risk)")
    print()
    
    # Demo 3: Sector Comparison
    print("Demo 3: Same Features Across Different Sectors")
    print("-" * 70)
    medium_risk = NormalizedFeatures(
        revenue_stability=0.65,
        transaction_velocity=0.60,
        liquidity_ratio=0.55,
        employment_consistency=0.70,
        compliance_score=0.75,
        growth_indicator=0.50,
        missing_sources=[]
    )
    
    trader_score = model.compute_score(medium_risk, 'Trader')
    manufacturer_score = model.compute_score(medium_risk, 'Manufacturer')
    services_score = model.compute_score(medium_risk, 'Services')
    
    print(f"Trader Score: {trader_score:.2f} (emphasizes transaction velocity)")
    print(f"Manufacturer Score: {manufacturer_score:.2f} (emphasizes revenue stability)")
    print(f"Services Score: {services_score:.2f} (emphasizes employment consistency)")
    print()
    
    # Demo 4: Missing Features
    print("Demo 4: Partial Data with Missing EPFO (Trader)")
    print("-" * 70)
    partial_data = NormalizedFeatures(
        revenue_stability=0.75,
        transaction_velocity=0.70,
        liquidity_ratio=0.68,
        employment_consistency=0.50,  # Not used due to missing EPFO
        compliance_score=0.85,
        growth_indicator=0.60,
        missing_sources=['EPFO']
    )
    
    available_features = [
        'revenue_stability',
        'transaction_velocity',
        'liquidity_ratio'
    ]
    
    full_score = model.compute_score(partial_data, 'Trader')
    partial_score = model.compute_score(partial_data, 'Trader', available_features)
    
    print(f"Score with all features: {full_score:.2f}")
    print(f"Score with partial data: {partial_score:.2f}")
    print(f"Difference: {abs(full_score - partial_score):.2f}")
    print("(Weights redistributed: rev=0.28, trans=0.39, liq=0.33)")
    print()
    
    # Demo 5: Weight Configuration
    print("Demo 5: Sector Weight Configurations")
    print("-" * 70)
    for sector in ['Trader', 'Manufacturer', 'Services']:
        weights = model.get_sector_weights(sector)
        print(f"\n{sector}:")
        print(f"  Revenue Stability: {weights.revenue_stability:.2f}")
        print(f"  Transaction Velocity: {weights.transaction_velocity:.2f}")
        print(f"  Liquidity Ratio: {weights.liquidity_ratio:.2f}")
        print(f"  Employment Consistency: {weights.employment_consistency:.2f}")
        print(f"  (Compliance & Growth have 0.0 weights - rolled into other features)")
    
    print()
    print("=" * 70)
    print("Demo Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()
