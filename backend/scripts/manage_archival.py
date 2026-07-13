#!/usr/bin/env python3
"""
CLI script for managing score history archival and retention policy.

Usage:
    python scripts/manage_archival.py --check-retention
    python scripts/manage_archival.py --storage-stats
    python scripts/manage_archival.py --archive --dry-run
    python scripts/manage_archival.py --archive --months 12
"""
import sys
import argparse
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from storage.archival import ScoreHistoryArchival
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description='Manage score history archival and retention policy'
    )
    
    parser.add_argument(
        '--check-retention',
        action='store_true',
        help='Check if 6-month minimum retention policy is satisfied'
    )
    
    parser.add_argument(
        '--storage-stats',
        action='store_true',
        help='Display storage statistics for score history'
    )
    
    parser.add_argument(
        '--archive',
        action='store_true',
        help='Archive records older than specified months'
    )
    
    parser.add_argument(
        '--months',
        type=int,
        default=12,
        help='Age threshold in months for archival (default: 12)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without making changes (recommended)'
    )
    
    args = parser.parse_args()
    
    # Initialize archival manager
    try:
        archival = ScoreHistoryArchival()
    except Exception as e:
        print(f"Error: Failed to initialize archival manager: {str(e)}")
        print("Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        sys.exit(1)
    
    # Execute requested operation
    try:
        if args.check_retention:
            print("Checking retention policy compliance...")
            result = archival.enforce_minimum_retention(min_months=6)
            
            print(f"\nRetention Policy Status:")
            print(f"  Compliant: {'✓ Yes' if result['compliant'] else '✗ No'}")
            print(f"  Total MSMEs: {result['msme_count']}")
            
            if result['non_compliant_msmes']:
                print(f"  Non-compliant MSMEs ({len(result['non_compliant_msmes'])}):")
                for msme_id in result['non_compliant_msmes']:
                    print(f"    - {msme_id}")
            else:
                print(f"  All MSMEs have at least 6 months of history ✓")
        
        elif args.storage_stats:
            print("Retrieving storage statistics...")
            stats = archival.get_storage_stats()
            
            print(f"\nScore History Storage Statistics:")
            print(f"  Total Records: {stats['total_records']}")
            print(f"  Unique MSMEs: {stats['unique_msmes']}")
            
            if stats['oldest_record_date']:
                oldest = datetime.fromisoformat(stats['oldest_record_date'].replace('Z', '+00:00'))
                print(f"  Oldest Record: {oldest.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if stats['newest_record_date']:
                newest = datetime.fromisoformat(stats['newest_record_date'].replace('Z', '+00:00'))
                print(f"  Newest Record: {newest.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"  Records Older Than 12 Months: {stats['records_older_than_12_months']}")
            
            if stats['records_older_than_12_months'] > 0:
                print(f"\n  ⚠ Warning: {stats['records_older_than_12_months']} records are eligible for archival")
                print(f"  Run: python scripts/manage_archival.py --archive --dry-run")
        
        elif args.archive:
            dry_run_label = " (DRY RUN)" if args.dry_run else ""
            print(f"Starting archival process{dry_run_label}...")
            print(f"Archive threshold: {args.months} months")
            
            result = archival.archive_old_records(months=args.months, dry_run=args.dry_run)
            
            print(f"\nArchival Results:")
            print(f"  Records Found: {result['records_found']}")
            print(f"  Cutoff Date: {result['cutoff_date']}")
            
            if result['oldest_record']:
                oldest = datetime.fromisoformat(result['oldest_record'].replace('Z', '+00:00'))
                print(f"  Oldest Record: {oldest.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if args.dry_run:
                print(f"\n  ℹ DRY RUN: No changes made")
                print(f"  To actually archive, run without --dry-run flag:")
                print(f"  python scripts/manage_archival.py --archive --months {args.months}")
            else:
                print(f"  Records Archived: {result['records_archived']}")
                print(f"  ✓ Archival complete")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
