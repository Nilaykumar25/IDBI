"""
Test Feature Engineering Pipeline
Validates feature computation, imputation, and normalization
"""
import sys
from datetime import datetime
from adapters.base_adapter import NormalizedData
from scoring.feature_engineering import (
    FeatureEngineeringPipeline, 
    EngineeredFeatures, 
    NormalizedFeatures
)


def test_revenue_stability():
    """Test revenue stability calculation"""
    print("\n=== Testing Revenue Stability ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Test case 1: Moderate growth (should be high stability)
    gst_data = NormalizedData(
        source='GST',
        fetched_at=datetime.now(),
        data={
            'annual_revenue': 25_000_000,
            'filing_frequency': 0.92,
            'compliance_status': 'compliant',
            'revenue_growth_rate': 8.5,  # Moderate positive growth
            'last_filing_date': datetime.now()
        }
    )
    
    stability = pipeline._compute_revenue_stability(gst_data)
    print(f"Moderate growth (8.5%): {stability:.3f} (expected: ~0.8-0.9)")
    assert 0.75 <= stability <= 0.95, f"Unexpected stability: {stability}"
    
    # Test case 2: High volatility (should be low stability)
    gst_data.data['revenue_growth_rate'] = 45.0  # High growth
    stability = pipeline._compute_revenue_stability(gst_data)
    print(f"High growth (45%): {stability:.3f} (expected: ~0.3-0.5)")
    assert 0.2 <= stability <= 0.6, f"Unexpected stability: {stability}"
    
    # Test case 3: Negative growth
    gst_data.data['revenue_growth_rate'] = -15.0
    stability = pipeline._compute_revenue_stability(gst_data)
    print(f"Negative growth (-15%): {stability:.3f} (expected: ~0.5-0.7)")
    assert 0.4 <= stability <= 0.8, f"Unexpected stability: {stability}"
    
    print("✓ Revenue stability tests passed")


def test_transaction_velocity():
    """Test transaction velocity calculation"""
    print("\n=== Testing Transaction Velocity ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Test case 1: High volume and frequency
    upi_data = NormalizedData(
        source='UPI',
        fetched_at=datetime.now(),
        data={
            'monthly_transaction_volume': 25_000_000,  # Mid-range
            'transaction_frequency': 450,  # Mid-range
            'average_transaction_value': 55_555,
            'inbound_outbound_ratio': 1.2,
            'transaction_growth_rate': 5.0
        }
    )
    
    velocity = pipeline._compute_transaction_velocity(upi_data)
    print(f"Mid-range volume & frequency: {velocity:.3f} (expected: ~0.5)")
    assert 0.3 <= velocity <= 0.7, f"Unexpected velocity: {velocity}"
    
    # Test case 2: Low volume and frequency
    upi_data.data['monthly_transaction_volume'] = 500_000
    upi_data.data['transaction_frequency'] = 50
    velocity = pipeline._compute_transaction_velocity(upi_data)
    print(f"Low volume & frequency: {velocity:.3f} (expected: <0.3)")
    assert velocity < 0.4, f"Unexpected velocity: {velocity}"
    
    # Test case 3: High volume and frequency
    upi_data.data['monthly_transaction_volume'] = 45_000_000
    upi_data.data['transaction_frequency'] = 750
    velocity = pipeline._compute_transaction_velocity(upi_data)
    print(f"High volume & frequency: {velocity:.3f} (expected: >0.7)")
    assert velocity > 0.6, f"Unexpected velocity: {velocity}"
    
    print("✓ Transaction velocity tests passed")


def test_liquidity_ratio():
    """Test liquidity ratio calculation"""
    print("\n=== Testing Liquidity Ratio ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Test case 1: Good liquidity
    aa_data = NormalizedData(
        source='AA',
        fetched_at=datetime.now(),
        data={
            'average_balance': 2_000_000,
            'minimum_balance': 500_000,
            'credit_debit_ratio': 1.15,
            'liquidity_ratio': 0.75,  # Good liquidity
            'overdraft_frequency': 0
        }
    )
    
    liquidity = pipeline._compute_liquidity_ratio(aa_data)
    print(f"Good liquidity (0.75): {liquidity:.3f}")
    assert liquidity == 0.75, f"Unexpected liquidity: {liquidity}"
    
    # Test case 2: Low liquidity
    aa_data.data['liquidity_ratio'] = 0.25
    liquidity = pipeline._compute_liquidity_ratio(aa_data)
    print(f"Low liquidity (0.25): {liquidity:.3f}")
    assert liquidity == 0.25, f"Unexpected liquidity: {liquidity}"
    
    # Test case 3: Excellent liquidity (capped at 1.0)
    aa_data.data['liquidity_ratio'] = 1.5
    liquidity = pipeline._compute_liquidity_ratio(aa_data)
    print(f"Excellent liquidity (1.5 → capped): {liquidity:.3f} (expected: 1.0)")
    assert liquidity == 1.0, f"Unexpected liquidity: {liquidity}"
    
    print("✓ Liquidity ratio tests passed")


def test_employment_consistency():
    """Test employment consistency calculation"""
    print("\n=== Testing Employment Consistency ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Test case 1: Stable employment
    epfo_data = NormalizedData(
        source='EPFO',
        fetched_at=datetime.now(),
        data={
            'employee_count': 45,
            'monthly_contribution_amount': 54_000,
            'contribution_regularity': 0.92,
            'employee_growth_rate': 8.0,  # Moderate stable growth
            'average_wage_per_employee': 1200
        }
    )
    
    consistency = pipeline._compute_employment_consistency(epfo_data)
    print(f"Stable employment (8% growth, 92% regularity): {consistency:.3f} (expected: >0.7)")
    assert consistency > 0.6, f"Unexpected consistency: {consistency}"
    
    # Test case 2: High churn
    epfo_data.data['employee_growth_rate'] = 35.0  # High volatility
    epfo_data.data['contribution_regularity'] = 0.70
    consistency = pipeline._compute_employment_consistency(epfo_data)
    print(f"High churn (35% growth, 70% regularity): {consistency:.3f} (expected: <0.6)")
    assert consistency < 0.7, f"Unexpected consistency: {consistency}"
    
    print("✓ Employment consistency tests passed")


def test_compliance_score():
    """Test compliance score calculation"""
    print("\n=== Testing Compliance Score ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Test case 1: Compliant
    gst_data = NormalizedData(
        source='GST',
        fetched_at=datetime.now(),
        data={
            'annual_revenue': 25_000_000,
            'filing_frequency': 0.92,
            'compliance_status': 'compliant',
            'revenue_growth_rate': 8.5,
            'last_filing_date': datetime.now()
        }
    )
    
    compliance = pipeline._compute_compliance_score(gst_data)
    print(f"Compliant (92% filing): {compliance:.3f} (expected: ~0.92)")
    assert 0.85 <= compliance <= 1.0, f"Unexpected compliance: {compliance}"
    
    # Test case 2: Partial compliance
    gst_data.data['compliance_status'] = 'partial'
    gst_data.data['filing_frequency'] = 0.75
    compliance = pipeline._compute_compliance_score(gst_data)
    print(f"Partial (75% filing): {compliance:.3f} (expected: ~0.525)")
    assert 0.4 <= compliance <= 0.7, f"Unexpected compliance: {compliance}"
    
    # Test case 3: Non-compliant
    gst_data.data['compliance_status'] = 'non-compliant'
    gst_data.data['filing_frequency'] = 0.50
    compliance = pipeline._compute_compliance_score(gst_data)
    print(f"Non-compliant (50% filing): {compliance:.3f} (expected: ~0.15)")
    assert compliance <= 0.3, f"Unexpected compliance: {compliance}"
    
    print("✓ Compliance score tests passed")


def test_growth_indicator():
    """Test growth indicator calculation"""
    print("\n=== Testing Growth Indicator ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Test case 1: Positive growth across all sources
    gst_data = NormalizedData(
        source='GST',
        fetched_at=datetime.now(),
        data={'revenue_growth_rate': 15.0}
    )
    
    upi_data = NormalizedData(
        source='UPI',
        fetched_at=datetime.now(),
        data={'transaction_growth_rate': 12.0}
    )
    
    epfo_data = NormalizedData(
        source='EPFO',
        fetched_at=datetime.now(),
        data={'employee_growth_rate': 10.0}
    )
    
    growth = pipeline._compute_growth_indicator(gst_data, upi_data, epfo_data)
    print(f"Positive growth (15%, 12%, 10%): {growth:.3f} (expected: >0.6)")
    assert growth > 0.6, f"Unexpected growth: {growth}"
    
    # Test case 2: Negative growth
    gst_data.data['revenue_growth_rate'] = -10.0
    upi_data.data['transaction_growth_rate'] = -8.0
    epfo_data.data['employee_growth_rate'] = -5.0
    growth = pipeline._compute_growth_indicator(gst_data, upi_data, epfo_data)
    print(f"Negative growth (-10%, -8%, -5%): {growth:.3f} (expected: <0.5)")
    assert growth < 0.5, f"Unexpected growth: {growth}"
    
    # Test case 3: Partial data (only GST)
    growth = pipeline._compute_growth_indicator(gst_data, None, None)
    print(f"Partial data (only GST): {growth:.3f}")
    assert growth is not None, "Growth should be computable with partial data"
    
    print("✓ Growth indicator tests passed")


def test_full_pipeline():
    """Test complete pipeline with all adapters"""
    print("\n=== Testing Full Pipeline ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Create complete data map
    data_map = {
        'GST': NormalizedData(
            source='GST',
            fetched_at=datetime.now(),
            data={
                'annual_revenue': 25_000_000,
                'filing_frequency': 0.92,
                'compliance_status': 'compliant',
                'revenue_growth_rate': 12.5,
                'last_filing_date': datetime.now()
            }
        ),
        'UPI': NormalizedData(
            source='UPI',
            fetched_at=datetime.now(),
            data={
                'monthly_transaction_volume': 8_000_000,
                'transaction_frequency': 350,
                'average_transaction_value': 22_857,
                'inbound_outbound_ratio': 1.25,
                'transaction_growth_rate': 8.5
            }
        ),
        'AA': NormalizedData(
            source='AA',
            fetched_at=datetime.now(),
            data={
                'average_balance': 1_500_000,
                'minimum_balance': 400_000,
                'credit_debit_ratio': 1.20,
                'liquidity_ratio': 0.68,
                'overdraft_frequency': 0
            }
        ),
        'EPFO': NormalizedData(
            source='EPFO',
            fetched_at=datetime.now(),
            data={
                'employee_count': 35,
                'monthly_contribution_amount': 42_000,
                'contribution_regularity': 0.92,
                'employee_growth_rate': 10.0,
                'average_wage_per_employee': 1200
            }
        )
    }
    
    # Compute features
    features = pipeline.compute_features(data_map)
    print(f"\nEngineered Features:")
    print(f"  Revenue Stability: {features.revenue_stability:.3f}")
    print(f"  Transaction Velocity: {features.transaction_velocity:.3f}")
    print(f"  Liquidity Ratio: {features.liquidity_ratio:.3f}")
    print(f"  Employment Consistency: {features.employment_consistency:.3f}")
    print(f"  Compliance Score: {features.compliance_score:.3f}")
    print(f"  Growth Indicator: {features.growth_indicator:.3f}")
    print(f"  Missing Sources: {features.missing_sources}")
    
    # Impute (should be no-op since all data present)
    imputed = pipeline.impute_missing_features(features)
    print(f"\nImputed Features: (should be same as above)")
    print(f"  Missing Sources: {imputed.missing_sources}")
    
    # Normalize
    normalized = pipeline.normalize_features(imputed)
    print(f"\nNormalized Features (0-1 scale):")
    print(f"  Revenue Stability: {normalized.revenue_stability:.3f}")
    print(f"  Transaction Velocity: {normalized.transaction_velocity:.3f}")
    print(f"  Liquidity Ratio: {normalized.liquidity_ratio:.3f}")
    print(f"  Employment Consistency: {normalized.employment_consistency:.3f}")
    print(f"  Compliance Score: {normalized.compliance_score:.3f}")
    print(f"  Growth Indicator: {normalized.growth_indicator:.3f}")
    
    # Validate all features are in 0-1 range
    assert 0 <= normalized.revenue_stability <= 1
    assert 0 <= normalized.transaction_velocity <= 1
    assert 0 <= normalized.liquidity_ratio <= 1
    assert 0 <= normalized.employment_consistency <= 1
    assert 0 <= normalized.compliance_score <= 1
    assert 0 <= normalized.growth_indicator <= 1
    
    print("✓ Full pipeline test passed")


def test_partial_data_scenario():
    """Test pipeline with missing data sources"""
    print("\n=== Testing Partial Data Scenario ===")
    
    pipeline = FeatureEngineeringPipeline()
    
    # Create data map with missing EPFO and UPI
    data_map = {
        'GST': NormalizedData(
            source='GST',
            fetched_at=datetime.now(),
            data={
                'annual_revenue': 25_000_000,
                'filing_frequency': 0.85,
                'compliance_status': 'partial',
                'revenue_growth_rate': 8.0,
                'last_filing_date': datetime.now()
            }
        ),
        'AA': NormalizedData(
            source='AA',
            fetched_at=datetime.now(),
            data={
                'average_balance': 1_200_000,
                'minimum_balance': 300_000,
                'credit_debit_ratio': 1.10,
                'liquidity_ratio': 0.55,
                'overdraft_frequency': 1
            }
        )
    }
    
    # Compute features
    features = pipeline.compute_features(data_map)
    print(f"\nEngineered Features (with missing UPI and EPFO):")
    print(f"  Revenue Stability: {features.revenue_stability}")
    print(f"  Transaction Velocity: {features.transaction_velocity}")
    print(f"  Liquidity Ratio: {features.liquidity_ratio}")
    print(f"  Employment Consistency: {features.employment_consistency}")
    print(f"  Compliance Score: {features.compliance_score}")
    print(f"  Growth Indicator: {features.growth_indicator}")
    print(f"  Missing Sources: {features.missing_sources}")
    
    assert 'UPI' in features.missing_sources
    assert 'EPFO' in features.missing_sources
    assert features.transaction_velocity is None
    assert features.employment_consistency is None
    
    # Impute missing features
    imputed = pipeline.impute_missing_features(features)
    print(f"\nImputed Features:")
    print(f"  Transaction Velocity: {imputed.transaction_velocity:.3f} (imputed)")
    print(f"  Employment Consistency: {imputed.employment_consistency:.3f} (imputed)")
    
    assert imputed.transaction_velocity == 0.3  # Default imputation
    assert imputed.employment_consistency == 0.5  # Default imputation
    
    # Normalize
    normalized = pipeline.normalize_features(imputed)
    print(f"\nNormalized Features:")
    print(f"  All features in 0-1 range: ✓")
    
    # Validate all features are in 0-1 range
    assert 0 <= normalized.revenue_stability <= 1
    assert 0 <= normalized.transaction_velocity <= 1
    assert 0 <= normalized.liquidity_ratio <= 1
    assert 0 <= normalized.employment_consistency <= 1
    assert 0 <= normalized.compliance_score <= 1
    assert 0 <= normalized.growth_indicator <= 1
    
    print("✓ Partial data scenario test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Feature Engineering Pipeline Test Suite")
    print("=" * 60)
    
    try:
        test_revenue_stability()
        test_transaction_velocity()
        test_liquidity_ratio()
        test_employment_consistency()
        test_compliance_score()
        test_growth_indicator()
        test_full_pipeline()
        test_partial_data_scenario()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
