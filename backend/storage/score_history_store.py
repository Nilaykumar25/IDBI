"""
ScoreHistoryStore class for persisting and retrieving MSME financial health scores.
Uses Supabase as the PostgreSQL backend for score history management.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from config import Config


class ScoreHistoryStore:
    """
    Manages persistence and retrieval of MSME financial health score history.
    
    Implements 6-12 month retention policy:
    - Minimum 6 months retention required for Trend Analysis View
    - Records older than 12 months should be archived
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize ScoreHistoryStore with Supabase client.
        
        Args:
            supabase_url: Supabase project URL (defaults to Config.SUPABASE_URL)
            supabase_key: Supabase service role key (defaults to Config.SUPABASE_KEY)
        """
        self.supabase_url = supabase_url or Config.SUPABASE_URL
        self.supabase_key = supabase_key or Config.SUPABASE_KEY
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be provided")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def save(self, score_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a score computation result to the database.
        
        Args:
            score_result: Dictionary containing score computation results with keys:
                - msme_id (str): MSME identifier
                - composite_score (float): Weighted composite score (0-100)
                - risk_band (str): Risk classification ('Low', 'Medium', 'High')
                - ml_confidence (dict): ML confidence scores {low, medium, high}
                - features (dict): Normalized feature values (0-1)
                - shap_values (dict): SHAP explainability values
                - missing_sources (list): List of failed data sources
                - sector (str): MSME sector ('Trader', 'Manufacturer', 'Services')
                - computed_at (datetime, optional): Timestamp (defaults to now)
        
        Returns:
            Dictionary containing the inserted record with generated ID
        
        Raises:
            ValueError: If required fields are missing or invalid
            Exception: If database insertion fails
        """
        # Validate required fields
        required_fields = ['msme_id', 'composite_score', 'risk_band', 'features', 'shap_values', 'sector']
        missing_fields = [field for field in required_fields if field not in score_result]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Prepare record for insertion
        record = {
            'msme_id': score_result['msme_id'],
            'composite_score': float(score_result['composite_score']),
            'risk_band': score_result['risk_band'],
            'ml_confidence_low': float(score_result.get('ml_confidence', {}).get('low', 0.0)),
            'ml_confidence_medium': float(score_result.get('ml_confidence', {}).get('medium', 0.0)),
            'ml_confidence_high': float(score_result.get('ml_confidence', {}).get('high', 0.0)),
            'features': score_result['features'],
            'shap_values': score_result['shap_values'],
            'missing_sources': score_result.get('missing_sources', []),
            'sector': score_result['sector'],
            'computed_at': score_result.get('computed_at', datetime.now()).isoformat()
        }
        
        # Insert into Supabase
        try:
            response = self.client.table('score_history').insert(record).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to insert score history record")
        
        except Exception as e:
            raise Exception(f"Database insertion failed: {str(e)}")
    
    def retrieve(self, msme_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most recent score for a given MSME.
        
        Args:
            msme_id: MSME identifier
        
        Returns:
            Dictionary containing the most recent score record, or None if not found
        """
        try:
            response = (
                self.client.table('score_history')
                .select('*')
                .eq('msme_id', msme_id)
                .order('computed_at', desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                return None
        
        except Exception as e:
            raise Exception(f"Failed to retrieve score history: {str(e)}")
    
    def retrieve_history(
        self, 
        msme_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical scores for a given MSME within a date range.
        
        Args:
            msme_id: MSME identifier
            start_date: Start of date range (defaults to 6 months ago)
            end_date: End of date range (defaults to now)
        
        Returns:
            List of score records ordered by computed_at (most recent first)
        """
        # Default to 6 months of history if no start date provided
        if start_date is None:
            start_date = datetime.now() - timedelta(days=180)
        
        if end_date is None:
            end_date = datetime.now()
        
        try:
            query = (
                self.client.table('score_history')
                .select('*')
                .eq('msme_id', msme_id)
                .gte('computed_at', start_date.isoformat())
                .lte('computed_at', end_date.isoformat())
                .order('computed_at', desc=True)
            )
            
            response = query.execute()
            
            return response.data if response.data else []
        
        except Exception as e:
            raise Exception(f"Failed to retrieve score history: {str(e)}")
    
    def get_all_msme_ids(self) -> List[str]:
        """
        Retrieve a list of all unique MSME IDs with score history.
        
        Returns:
            List of unique MSME identifiers
        """
        try:
            response = (
                self.client.table('score_history')
                .select('msme_id')
                .execute()
            )
            
            if response.data:
                # Extract unique MSME IDs
                msme_ids = list(set(record['msme_id'] for record in response.data))
                return msme_ids
            else:
                return []
        
        except Exception as e:
            raise Exception(f"Failed to retrieve MSME IDs: {str(e)}")
    
    def count_records(self, msme_id: Optional[str] = None) -> int:
        """
        Count score history records.
        
        Args:
            msme_id: Optional MSME identifier to count records for specific MSME
        
        Returns:
            Count of score history records
        """
        try:
            query = self.client.table('score_history').select('id', count='exact')
            
            if msme_id:
                query = query.eq('msme_id', msme_id)
            
            response = query.execute()
            
            return response.count if hasattr(response, 'count') else 0
        
        except Exception as e:
            raise Exception(f"Failed to count records: {str(e)}")
