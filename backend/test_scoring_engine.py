"""
Test script for ScoringEngine
Verifies orchestration and integration
"""
import sys
sys.path.insert(0, '.')

from scoring.scoring_engine import ScoringEngine, MSMEIdentifiers

def test_scoring_engine():
    """Test scoring engine with mock data"""
    print("Testing Scoring Engine...")
    print("-" * 60)
    
    # Initialize scoring engine in mock mode
    engine = ScoringEngine(mode='mock', model_dir='models')
    print("✓ Scoring engine initialized")
    
    # Create test MSME identifiers
    identifiers = MSMEIdentifiers(
        msme_id="TEST-MSME-001",
        gst_number="29AABCT1332L1Z5",
        upi_id="merchant@paytm",
        aa_consent_token="mock-consent-token",
        epfo_establishment_id="TNCHE0012345",
        sector="Trader"
    )
    print(f"✓ Test identifiers created for {identifiers.msme_id}")
    
    # Compute score
    print("\nComputing score...")
    result = engine.compute_score(identifiers)
    
    print("\n" + "=" * 60)
    print("SCORE COMPUTATION RESULT")
    print("=" * 60)
    print(f"MSME ID: {result.msme_id}")
    print(f"Sector: {result.sector}")
    print(f"Composite Score: {result.composite_score:.2f}/100")
    print(f"Risk Band: {result.ml_risk_band}")
    print(f"\nConfidence:")
    print(f"  Low:    {result.ml_confidence.low:.2%}")
    print(f"  Medium: {result.ml_confidence.medium:.2%}")
    print(f"  High:   {result.ml_confidence.high:.2%}")
    
    print(f"\nFeatures:")
    print(f"  Revenue Stability:      {result.features.revenue_stability:.3f}")
    print(f"  Transaction Velocity:   {result.features.transaction_velocity:.3f}")
    print(f"  Liquidity Ratio:        {result.features.liquidity_ratio:.3f}")
    print(f"  Employment Consistency: {result.features.employment_consistency:.3f}")
    print(f"  Compliance Score:       {result.features.compliance_score:.3f}")
    print(f"  Growth Indicator:       {result.features.growth_indicator:.3f}")
    
    print(f"\nSHAP Values (Feature Contributions):")
    ranked_features = result.shap_values.get_ranked_features()
    for feature_name, shap_value in ranked_features:
        direction = "→" if shap_value >= 0 else "←"
        print(f"  {feature_name:25s} {direction} {shap_value:+.4f}")
    
    if result.missing_data_sources:
        print(f"\n⚠ Missing Data Sources: {', '.join(result.missing_data_sources)}")
    else:
        print(f"\n✓ All data sources available")
    
    print(f"\nComputed at: {result.computed_at.isoformat()}")
    print("=" * 60)
    
    print("\n✓ Scoring engine test completed successfully!")
    
    # Test partial data scenario
    print("\n" + "=" * 60)
    print("TESTING WHAT-IF SIMULATION")
    print("=" * 60)
    
    from scoring.feature_engineering import NormalizedFeatures
    
    # Create adjusted features
    adjusted_features = NormalizedFeatures(
        revenue_stability=0.9,
        transaction_velocity=0.85,
        liquidity_ratio=0.8,
        employment_consistency=0.75,
        compliance_score=0.95,
        growth_indicator=0.7,
        missing_sources=[]
    )
    
    print("Simulating with improved features...")
    sim_result = engine.compute_with_partial_data(adjusted_features, "Trader")
    
    print(f"\nSimulated Score: {sim_result.composite_score:.2f}/100")
    print(f"Simulated Risk Band: {sim_result.ml_risk_band}")
    print(f"Score Delta: {sim_result.composite_score - result.composite_score:+.2f}")
    
    print("\n✓ What-if simulation test completed successfully!")

if __name__ == '__main__':
    try:
        test_scoring_engine()
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
