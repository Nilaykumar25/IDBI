#!/usr/bin/env python3
"""
Generate Synthetic Dataset Script
Produces 500-1000 synthetic MSME profiles for ML training
"""
import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scoring.synthetic_dataset_generator import SyntheticDatasetGenerator


def main():
    """Main entry point for dataset generation"""
    parser = argparse.ArgumentParser(
        description='Generate synthetic MSME dataset for ML training'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=1000,
        help='Number of profiles to generate (default: 1000)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='synthetic_dataset',
        help='Output filename without extension (default: synthetic_dataset)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    parser.add_argument(
        '--low-pct',
        type=float,
        default=0.5,
        help='Percentage of Low risk profiles (default: 0.5 = 50%%)'
    )
    parser.add_argument(
        '--medium-pct',
        type=float,
        default=0.3,
        help='Percentage of Medium risk profiles (default: 0.3 = 30%%)'
    )
    parser.add_argument(
        '--high-pct',
        type=float,
        default=0.2,
        help='Percentage of High risk profiles (default: 0.2 = 20%%)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility (optional)'
    )
    
    args = parser.parse_args()
    
    # Validate size
    if args.size < 100:
        print(f"Error: Size must be at least 100, got {args.size}")
        return 1
    
    if args.size > 10000:
        print(f"Warning: Generating {args.size} profiles (recommended: 500-1000)")
    
    # Validate percentages
    total_pct = args.low_pct + args.medium_pct + args.high_pct
    if abs(total_pct - 1.0) > 0.01:
        print(f"Error: Percentages must sum to 1.0, got {total_pct}")
        return 1
    
    print(f"Generating {args.size} synthetic MSME profiles...")
    print(f"Distribution: {args.low_pct*100:.0f}% Low, {args.medium_pct*100:.0f}% Medium, {args.high_pct*100:.0f}% High")
    
    # Initialize generator
    generator = SyntheticDatasetGenerator(seed=args.seed)
    
    # Generate dataset
    profiles = generator.generate_dataset(
        size=args.size,
        low_pct=args.low_pct,
        medium_pct=args.medium_pct,
        high_pct=args.high_pct
    )
    
    print(f"Generated {len(profiles)} profiles")
    
    # Count by risk band
    low_count = sum(1 for p in profiles if p.risk_band == 'Low')
    medium_count = sum(1 for p in profiles if p.risk_band == 'Medium')
    high_count = sum(1 for p in profiles if p.risk_band == 'High')
    
    print(f"  Low risk: {low_count} ({low_count/len(profiles)*100:.1f}%)")
    print(f"  Medium risk: {medium_count} ({medium_count/len(profiles)*100:.1f}%)")
    print(f"  High risk: {high_count} ({high_count/len(profiles)*100:.1f}%)")
    
    # Count by sector
    trader_count = sum(1 for p in profiles if p.sector == 'Trader')
    mfg_count = sum(1 for p in profiles if p.sector == 'Manufacturer')
    services_count = sum(1 for p in profiles if p.sector == 'Services')
    
    print(f"  Trader: {trader_count} ({trader_count/len(profiles)*100:.1f}%)")
    print(f"  Manufacturer: {mfg_count} ({mfg_count/len(profiles)*100:.1f}%)")
    print(f"  Services: {services_count} ({services_count/len(profiles)*100:.1f}%)")
    
    # Export to requested formats
    if args.format in ['csv', 'both']:
        csv_path = f"{args.output}.csv"
        generator.export_to_csv(profiles, csv_path)
        print(f"\nExported to CSV: {csv_path}")
    
    if args.format in ['json', 'both']:
        json_path = f"{args.output}.json"
        generator.export_to_json(profiles, json_path)
        print(f"Exported to JSON: {json_path}")
    
    print("\nDataset generation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
