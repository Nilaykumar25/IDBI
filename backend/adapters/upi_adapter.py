"""
UPI Data Adapter
Retrieves and normalizes UPI (Unified Payments Interface) transaction data for MSMEs
"""
import random
import time
from typing import Dict, Any, Literal, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_adapter import DataAdapter, NormalizedData


@dataclass
class UPINormalizedData(NormalizedData):
    """Normalized UPI data structure"""
    
    def __post_init__(self):
        self.source = 'UPI'
        if self.data is None:
            self.data = {}


class UPIAdapter(DataAdapter):
    """
    UPI Data Adapter implementation with mock data generation.
    Simulates realistic UPI transaction patterns with volume and frequency metrics.
    """
    
    def __init__(self):
        """Initialize UPI adapter"""
        super().__init__()
        self._mock_data_cache: Dict[str, Dict[str, Any]] = {}
    
    def fetch_data(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieves UPI transaction data for the given UPI ID.
        
        Args:
            identifier: UPI identification string
            
        Returns:
            Raw UPI transaction data dictionary
            
        Raises:
            Exception: If data retrieval fails (5% failure rate in mock mode)
        """
        # Simulate network latency (50-200ms)
        latency_ms = random.randint(50, 200)
        time.sleep(latency_ms / 1000.0)
        
        # Simulate 95% success rate
        if random.random() > 0.95:
            self._update_status(False, "Failed to retrieve UPI data: Service unavailable")
            raise Exception("Failed to retrieve UPI data: Service unavailable")
        
        # Return cached data if available, otherwise generate new
        if identifier not in self._mock_data_cache:
            self._mock_data_cache[identifier] = self._generate_mock_data(identifier)
        
        self._update_status(True)
        return self._mock_data_cache[identifier]
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> UPINormalizedData:
        """
        Normalizes raw UPI transaction data to standard format.
        
        Args:
            raw_data: Raw UPI data from fetch_data()
            
        Returns:
            UPINormalizedData object with standardized structure
        """
        transactions = raw_data['transactions']
        
        # Calculate monthly transaction volume (total value)
        monthly_volume = sum(t['amount'] for t in transactions)
        
        # Calculate transaction frequency (count per month)
        transaction_frequency = len(transactions)
        
        # Calculate average transaction value
        average_transaction_value = monthly_volume / transaction_frequency if transaction_frequency > 0 else 0
        
        # Calculate inbound/outbound ratio
        inbound_total = sum(t['amount'] for t in transactions if t['type'] == 'inbound')
        outbound_total = sum(t['amount'] for t in transactions if t['type'] == 'outbound')
        inbound_outbound_ratio = inbound_total / outbound_total if outbound_total > 0 else 0
        
        # Calculate transaction growth rate (month-over-month)
        current_month_volume = monthly_volume
        previous_month_volume = raw_data['previous_month_volume']
        transaction_growth_rate = ((current_month_volume / previous_month_volume) - 1) * 100 if previous_month_volume > 0 else 0
        
        return UPINormalizedData(
            source='UPI',
            fetched_at=datetime.now(),
            data={
                'monthly_transaction_volume': monthly_volume,
                'transaction_frequency': transaction_frequency,
                'average_transaction_value': average_transaction_value,
                'inbound_outbound_ratio': inbound_outbound_ratio,
                'transaction_growth_rate': transaction_growth_rate
            }
        )
    
    def _generate_mock_data(self, upi_id: str) -> Dict[str, Any]:
        """
        Generates realistic mock UPI transaction data with volume and frequency patterns.
        
        Args:
            upi_id: UPI identification string
            
        Returns:
            Dictionary containing mock UPI transaction data
        """
        # Generate number of transactions for the month (100-800 transactions)
        num_transactions = random.randint(100, 800)
        
        # Generate transactions with realistic patterns
        transactions: List[Dict[str, Any]] = []
        for i in range(num_transactions):
            # Random transaction type (60% inbound, 40% outbound for healthy business)
            transaction_type = 'inbound' if random.random() < 0.6 else 'outbound'
            
            # Generate transaction amount based on type
            if transaction_type == 'inbound':
                # Customer payments (typically smaller, more frequent)
                amount = random.uniform(500, 50000)
            else:
                # Vendor payments (typically larger, less frequent)
                amount = random.uniform(1000, 100000)
            
            # Random timestamp within the month
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            transactions.append({
                'transaction_id': f'UPI{i:06d}',
                'type': transaction_type,
                'amount': amount,
                'timestamp': timestamp
            })
        
        # Generate previous month volume for growth calculation
        current_month_volume = sum(t['amount'] for t in transactions)
        # Previous month volume with some variation (80-120% of current)
        previous_month_volume = current_month_volume * random.uniform(0.8, 1.2)
        
        return {
            'upi_id': upi_id,
            'transactions': transactions,
            'previous_month_volume': previous_month_volume
        }
