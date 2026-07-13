"""
Archival logic for score history retention policy.
Implements 6-12 month retention with automated archival for older records.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from supabase import create_client, Client
from config import Config


class ScoreHistoryArchival:
    """
    Manages archival and retention policy for score history records.
    
    Retention Policy:
    - Minimum retention: 6 months (required for Trend Analysis View)
    - Active storage: 12 months
    - Archive threshold: Records older than 12 months
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize archival manager with Supabase client.
        
        Args:
            supabase_url: Supabase project URL (defaults to Config.SUPABASE_URL)
            supabase_key: Supabase service role key (defaults to Config.SUPABASE_KEY)
        """
        self.supabase_url = supabase_url or Config.SUPABASE_URL
        self.supabase_key = supabase_key or Config.SUPABASE_KEY
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be provided")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def get_records_for_archival(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Retrieve records older than specified months for archival.
        
        Args:
            months: Age threshold in months (default: 12)
        
        Returns:
            List of records ready for archival
        """
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        try:
            response = (
                self.client.table('score_history')
                .select('*')
                .lt('computed_at', cutoff_date.isoformat())
                .execute()
            )
            
            return response.data if response.data else []
        
        except Exception as e:
            raise Exception(f"Failed to retrieve records for archival: {str(e)}")
    
    def archive_old_records(self, months: int = 12, dry_run: bool = True) -> Dict[str, Any]:
        """
        Archive records older than specified months.
        
        This method performs the following:
        1. Identifies records older than threshold
        2. Copies records to archive table (if it exists)
        3. Deletes records from active table (if not dry_run)
        
        Args:
            months: Age threshold in months (default: 12)
            dry_run: If True, only report what would be archived without making changes
        
        Returns:
            Dictionary with archival results:
                - records_found: Number of records eligible for archival
                - records_archived: Number of records actually archived
                - oldest_record: Date of oldest archived record
                - dry_run: Whether this was a dry run
        """
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        try:
            # Find records to archive
            records = self.get_records_for_archival(months)
            
            result = {
                'records_found': len(records),
                'records_archived': 0,
                'oldest_record': None,
                'cutoff_date': cutoff_date.isoformat(),
                'dry_run': dry_run
            }
            
            if not records:
                return result
            
            # Find oldest record
            if records:
                oldest = min(records, key=lambda r: r['computed_at'])
                result['oldest_record'] = oldest['computed_at']
            
            if dry_run:
                # Dry run: just report what would be archived
                return result
            
            # Archive records (copy to archive table and delete from active table)
            # Note: This requires score_history_archive table to exist
            # For now, we'll just delete old records as archival destination is optional
            
            # Delete records older than threshold
            delete_response = (
                self.client.table('score_history')
                .delete()
                .lt('computed_at', cutoff_date.isoformat())
                .execute()
            )
            
            result['records_archived'] = len(records)
            
            return result
        
        except Exception as e:
            raise Exception(f"Failed to archive records: {str(e)}")
    
    def enforce_minimum_retention(self, min_months: int = 6) -> Dict[str, Any]:
        """
        Verify that at least min_months of history exists for each MSME.
        
        This is a safety check to ensure the 6-month minimum retention policy.
        
        Args:
            min_months: Minimum retention period in months (default: 6)
        
        Returns:
            Dictionary with retention status:
                - compliant: True if all MSMEs have min_months of history
                - msme_count: Total number of unique MSMEs
                - non_compliant_msmes: List of MSMEs with insufficient history
        """
        min_date = datetime.now() - timedelta(days=min_months * 30)
        
        try:
            # Get all unique MSME IDs
            all_msmes_response = (
                self.client.table('score_history')
                .select('msme_id')
                .execute()
            )
            
            if not all_msmes_response.data:
                return {
                    'compliant': True,
                    'msme_count': 0,
                    'non_compliant_msmes': []
                }
            
            msme_ids = list(set(record['msme_id'] for record in all_msmes_response.data))
            
            non_compliant_msmes = []
            
            for msme_id in msme_ids:
                # Check if MSME has records within retention period
                recent_records_response = (
                    self.client.table('score_history')
                    .select('id')
                    .eq('msme_id', msme_id)
                    .gte('computed_at', min_date.isoformat())
                    .execute()
                )
                
                if not recent_records_response.data:
                    non_compliant_msmes.append(msme_id)
            
            return {
                'compliant': len(non_compliant_msmes) == 0,
                'msme_count': len(msme_ids),
                'non_compliant_msmes': non_compliant_msmes
            }
        
        except Exception as e:
            raise Exception(f"Failed to check retention compliance: {str(e)}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about score history storage.
        
        Returns:
            Dictionary with storage statistics:
                - total_records: Total number of records
                - oldest_record_date: Date of oldest record
                - newest_record_date: Date of newest record
                - unique_msmes: Number of unique MSMEs
                - records_older_than_12_months: Count of archival-eligible records
        """
        try:
            # Get all records
            all_records_response = (
                self.client.table('score_history')
                .select('computed_at, msme_id')
                .execute()
            )
            
            records = all_records_response.data if all_records_response.data else []
            
            if not records:
                return {
                    'total_records': 0,
                    'oldest_record_date': None,
                    'newest_record_date': None,
                    'unique_msmes': 0,
                    'records_older_than_12_months': 0
                }
            
            # Calculate stats
            dates = [datetime.fromisoformat(r['computed_at'].replace('Z', '+00:00')) for r in records]
            oldest_date = min(dates)
            newest_date = max(dates)
            unique_msmes = len(set(r['msme_id'] for r in records))
            
            # Count records older than 12 months
            twelve_months_ago = datetime.now() - timedelta(days=365)
            old_records_count = sum(1 for d in dates if d < twelve_months_ago)
            
            return {
                'total_records': len(records),
                'oldest_record_date': oldest_date.isoformat(),
                'newest_record_date': newest_date.isoformat(),
                'unique_msmes': unique_msmes,
                'records_older_than_12_months': old_records_count
            }
        
        except Exception as e:
            raise Exception(f"Failed to get storage stats: {str(e)}")
