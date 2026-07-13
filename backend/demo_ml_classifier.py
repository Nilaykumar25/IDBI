#!/usr/bin/env python3
"""
Demo script for ML Classifier
Demonstrates prediction and explainability features
"""
from scoring.ml_classifier import MLClassifier
from scoring.feature_engineering import NormalizedFeatures


def print_separator(title=""):
    """Print a separator line with optional title"""
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def main():
    """Main demo function"""
    print_separator("ML Classifier Demo")
    
    # Initialize and load classifier
    print("Loading ML classifier...")
    classifier = MLClassifier(model_dir='models')
    classifier.load_model(version='v1')
    print("✓ Model loaded successfully\n")
    
    # Demo 1: Low Risk Profile
    print_separator("Example 1: Low Risk Profile")
    
    low_risk_features = NormalizedFeatures(
        revenue_stability=0.85,
        transaction_velocity=0.80,
        liquidity_ratio=0.85,
        employment_consistency=0.82,
        compliance_score=0.90,
        growth_indicator=0.78,
        missing_sources=[]
    )
    
    print("Input Features:")
    print(f"  Revenue Stability:       {low_risk_features.revenue_stability:.2f}")
    print(f"  Transaction Velocity:    {low_risk_features.transaction_velocity:.2f}")
    print(f"  Liquidity Ratio:         {low_risk_features.liquidity_ratio:.2f}")
    print(f"  Employment Consistency:  {low_risk_features.employment_consistency:.2f}")
    print(f"  Compliance Score:        {low_risk_features.compliance_score:.2f}")
    print(f"  Growth Indicator:        {low_risk_features.growth_indicator:.2f}")
    
    prediction = classifier.predict(low_risk_features)
    print(f"\nPrediction:")
    print(f"  Risk Band: {prediction.risk_band}")
    print(f"  Confidence:")
    print(f"    Low:    {prediction.confidence.low:.4f} ({prediction.confidence.low*100:.2f}%)")
    print(f"    Medium: {prediction.confidence.medium:.4f} ({prediction.confidence.medium*100:.2f}%)")
    print(f"    High:   {prediction.confidence.high:.4f} ({prediction.confidence.high*100:.2f}%)")
    
    shap_values = classifier.explain_prediction(low_risk_features)
    ranked_features = shap_values.get_ranked_features()
    
    print(f"\nSHAP Explanation (Top Contributing Features):")
    for i, (feature, value) in enumerate(ranked_features[:3], 1):
        impact = "positive" if value > 0 else "negative"
        print(f"  {i}. {feature.replace('_', ' ').title()}: {value:+.4f} ({impact})")
    
    # Demo 2: High Risk Profile
    print_separator("Example 2: High Risk Profile")
    
    high_risk_features = NormalizedFeatures(
        revenue_stability=0.25,
        transaction_velocity=0.20,
        liquidity_ratio=0.15,
        employment_consistency=0.22,
        compliance_score=0.35,
        growth_indicator=0.18,
        missing_sources=[]
    )
    
    print("Input Features:")
    print(f"  Revenue Stability:       {high_risk_features.revenue_stability:.2f}")
    print(f"  Transaction Velocity:    {high_risk_features.transaction_velocity:.2f}")
    print(f"  Liquidity Ratio:         {high_risk_features.liquidity_ratio:.2f}")
    print(f"  Employment Consistency:  {high_risk_features.employment_consistency:.2f}")
    print(f"  Compliance Score:        {high_risk_features.compliance_score:.2f}")
    print(f"  Growth Indicator:        {high_risk_features.growth_indicator:.2f}")
    
    prediction = classifier.predict(high_risk_features)
    print(f"\nPrediction:")
    print(f"  Risk Band: {prediction.risk_band}")
    print(f"  Confidence:")
    print(f"    Low:    {prediction.confidence.low:.4f} ({prediction.confidence.low*100:.2f}%)")
    print(f"    Medium: {prediction.confidence.medium:.4f} ({prediction.confidence.medium*100:.2f}%)")
    print(f"    High:   {prediction.confidence.high:.4f} ({prediction.confidence.high*100:.2f}%)")
    
    shap_values = classifier.explain_prediction(high_risk_features)
    ranked_features = shap_values.get_ranked_features()
    
    print(f"\nSHAP Explanation (Top Contributing Features):")
    for i, (feature, value) in enumerate(ranked_features[:3], 1):
        impact = "positive" if value > 0 else "negative"
        print(f"  {i}. {feature.replace('_', ' ').title()}: {value:+.4f} ({impact})")
    
    # Demo 3: Medium Risk Profile
    print_separator("Example 3: Medium Risk Profile")
    
    medium_risk_features = NormalizedFeatures(
        revenue_stability=0.55,
        transaction_velocity=0.50,
        liquidity_ratio=0.45,
        employment_consistency=0.52,
        compliance_score=0.65,
        growth_indicator=0.48,
        missing_sources=[]
    )
    
    print("Input Features:")
    print(f"  Revenue Stability:       {medium_risk_features.revenue_stability:.2f}")
    print(f"  Transaction Velocity:    {medium_risk_features.transaction_velocity:.2f}")
    print(f"  Liquidity Ratio:         {medium_risk_features.liquidity_ratio:.2f}")
    print(f"  Employment Consistency:  {medium_risk_features.employment_consistency:.2f}")
    print(f"  Compliance Score:        {medium_risk_features.compliance_score:.2f}")
    print(f"  Growth Indicator:        {medium_risk_features.growth_indicator:.2f}")
    
    prediction = classifier.predict(medium_risk_features)
    print(f"\nPrediction:")
    print(f"  Risk Band: {prediction.risk_band}")
    print(f"  Confidence:")
    print(f"    Low:    {prediction.confidence.low:.4f} ({prediction.confidence.low*100:.2f}%)")
    print(f"    Medium: {prediction.confidence.medium:.4f} ({prediction.confidence.medium*100:.2f}%)")
    print(f"    High:   {prediction.confidence.high:.4f} ({prediction.confidence.high*100:.2f}%)")
    
    shap_values = classifier.explain_prediction(medium_risk_features)
    ranked_features = shap_values.get_ranked_features()
    
    print(f"\nSHAP Explanation (All Features Ranked by Impact):")
    for i, (feature, value) in enumerate(ranked_features, 1):
        impact = "positive" if value > 0 else "negative"
        print(f"  {i}. {feature.replace('_', ' ').title()}: {value:+.4f} ({impact})")
    
    print_separator()
    print("Demo completed successfully!")
    print("\nKey Takeaways:")
    print("  • The ML classifier predicts risk bands (Low/Medium/High)")
    print("  • Confidence scores show probability for each risk band")
    print("  • SHAP values explain which features drove the prediction")
    print("  • Positive SHAP values increase risk, negative values decrease risk")
    print()


if __name__ == '__main__':
    main()
