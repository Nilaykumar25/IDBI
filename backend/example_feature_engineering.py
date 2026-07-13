"""
Feature Engineering Pipeline Integration Example
Demonstrates how to use the feature engineering pipeline with data adapters
"""
from adapters.gst_adapter import GSTAdapter
from adapters.upi_adapter import UPIAdapter
from adapters.aa_adapter import AAAdapter
from adapters.epfo_adapter import EPFOAdapter
from scoring.feature_engineering import FeatureEngineeringPipeline


def main():
    """Example workflow: fetch data from adapters and compute features"""
    print("=" * 70)
    print("Feature Engineering Pipeline Integration Example")
    print("=" * 70)
    
    # Initialize adapters
    print("\n1. Initializing adapters...")
    gst_adapter = GSTAdapter()
    upi_adapter = UPIAdapter()
    aa_adapter = AAAdapter()
    epfo_adapter = EPFOAdapter()
    
    # Mock MSME identifiers
    msme_identifiers = {
        'gst_number': '29ABCDE1234F1Z5',
        'upi_id': 'business@upi',
        'aa_consent_token': 'consent-token-xyz',
        'epfo_establishment_id': 'EPFO12345'
    }
    
    # Fetch and normalize data from all adapters
    print("\n2. Fetching and normalizing data from adapters...")
    data_map = {}
    
    try:
        raw_gst = gst_adapter.fetch_data(msme_identifiers['gst_number'])
        data_map['GST'] = gst_adapter.normalize_data(raw_gst)
        print("   ✓ GST data retrieved")
    except Exception as e:
        print(f"   ✗ GST data failed: {e}")
    
    try:
        raw_upi = upi_adapter.fetch_data(msme_identifiers['upi_id'])
        data_map['UPI'] = upi_adapter.normalize_data(raw_upi)
        print("   ✓ UPI data retrieved")
    except Exception as e:
        print(f"   ✗ UPI data failed: {e}")
    
    try:
        raw_aa = aa_adapter.fetch_data(msme_identifiers['aa_consent_token'])
        data_map['AA'] = aa_adapter.normalize_data(raw_aa)
        print("   ✓ AA data retrieved")
    except Exception as e:
        print(f"   ✗ AA data failed: {e}")
    
    try:
        raw_epfo = epfo_adapter.fetch_data(msme_identifiers['epfo_establishment_id'])
        data_map['EPFO'] = epfo_adapter.normalize_data(raw_epfo)
        print("   ✓ EPFO data retrieved")
    except Exception as e:
        print(f"   ✗ EPFO data failed: {e}")
    
    # Initialize feature engineering pipeline
    print("\n3. Initializing feature engineering pipeline...")
    pipeline = FeatureEngineeringPipeline()
    
    # Compute features
    print("\n4. Computing engineered features...")
    features = pipeline.compute_features(data_map)
    
    print("\n   Raw Features:")
    print(f"   - Revenue Stability:       {features.revenue_stability:.4f}" if features.revenue_stability else "   - Revenue Stability:       MISSING")
    print(f"   - Transaction Velocity:    {features.transaction_velocity:.4f}" if features.transaction_velocity else "   - Transaction Velocity:    MISSING")
    print(f"   - Liquidity Ratio:         {features.liquidity_ratio:.4f}" if features.liquidity_ratio else "   - Liquidity Ratio:         MISSING")
    print(f"   - Employment Consistency:  {features.employment_consistency:.4f}" if features.employment_consistency else "   - Employment Consistency:  MISSING")
    print(f"   - Compliance Score:        {features.compliance_score:.4f}" if features.compliance_score else "   - Compliance Score:        MISSING")
    print(f"   - Growth Indicator:        {features.growth_indicator:.4f}" if features.growth_indicator else "   - Growth Indicator:        MISSING")
    
    if features.missing_sources:
        print(f"\n   ⚠ Missing data sources: {', '.join(features.missing_sources)}")
    
    # Impute missing features
    print("\n5. Imputing missing features...")
    imputed_features = pipeline.impute_missing_features(features)
    
    if features.missing_sources:
        print("   Imputed values applied for missing sources")
    else:
        print("   No imputation needed - all data sources available")
    
    # Normalize features
    print("\n6. Normalizing features to 0-1 scale...")
    normalized_features = pipeline.normalize_features(imputed_features)
    
    print("\n   Normalized Features (0-1 scale):")
    print(f"   - Revenue Stability:       {normalized_features.revenue_stability:.4f}")
    print(f"   - Transaction Velocity:    {normalized_features.transaction_velocity:.4f}")
    print(f"   - Liquidity Ratio:         {normalized_features.liquidity_ratio:.4f}")
    print(f"   - Employment Consistency:  {normalized_features.employment_consistency:.4f}")
    print(f"   - Compliance Score:        {normalized_features.compliance_score:.4f}")
    print(f"   - Growth Indicator:        {normalized_features.growth_indicator:.4f}")
    
    # Display underlying data for transparency
    print("\n" + "=" * 70)
    print("Underlying Data Summary")
    print("=" * 70)
    
    if 'GST' in data_map:
        gst_data = data_map['GST'].data
        print(f"\nGST Data:")
        print(f"  Annual Revenue:         ₹{gst_data['annual_revenue']:,.0f}")
        print(f"  Filing Frequency:       {gst_data['filing_frequency']*100:.1f}%")
        print(f"  Compliance Status:      {gst_data['compliance_status']}")
        print(f"  Revenue Growth Rate:    {gst_data['revenue_growth_rate']:.1f}%")
    
    if 'UPI' in data_map:
        upi_data = data_map['UPI'].data
        print(f"\nUPI Data:")
        print(f"  Monthly Volume:         ₹{upi_data['monthly_transaction_volume']:,.0f}")
        print(f"  Transaction Frequency:  {upi_data['transaction_frequency']} txns/month")
        print(f"  Avg Transaction Value:  ₹{upi_data['average_transaction_value']:,.0f}")
        print(f"  Inbound/Outbound Ratio: {upi_data['inbound_outbound_ratio']:.2f}")
        print(f"  Transaction Growth:     {upi_data['transaction_growth_rate']:.1f}%")
    
    if 'AA' in data_map:
        aa_data = data_map['AA'].data
        print(f"\nAccount Aggregator Data:")
        print(f"  Average Balance:        ₹{aa_data['average_balance']:,.0f}")
        print(f"  Minimum Balance:        ₹{aa_data['minimum_balance']:,.0f}")
        print(f"  Credit/Debit Ratio:     {aa_data['credit_debit_ratio']:.2f}")
        print(f"  Liquidity Ratio:        {aa_data['liquidity_ratio']:.2f}")
        print(f"  Overdraft Frequency:    {aa_data['overdraft_frequency']} times")
    
    if 'EPFO' in data_map:
        epfo_data = data_map['EPFO'].data
        print(f"\nEPFO Data:")
        print(f"  Employee Count:         {epfo_data['employee_count']}")
        print(f"  Monthly Contribution:   ₹{epfo_data['monthly_contribution_amount']:,.0f}")
        print(f"  Contribution Regularity:{epfo_data['contribution_regularity']*100:.1f}%")
        print(f"  Employee Growth Rate:   {epfo_data['employee_growth_rate']:.1f}%")
        print(f"  Avg Wage per Employee:  ₹{epfo_data['average_wage_per_employee']:,.0f}")
    
    print("\n" + "=" * 70)
    print("✓ Feature engineering pipeline completed successfully")
    print("=" * 70)
    print("\nNext steps:")
    print("  - Use normalized features for composite weighted scoring")
    print("  - Use normalized features for ML classifier prediction")
    print("  - Compute SHAP values for explainability")


if __name__ == "__main__":
    main()
