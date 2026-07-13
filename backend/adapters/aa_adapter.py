"""
Account Aggregator Data Adapter
Retrieves and normalizes bank account data via Account Aggregator framework for MSMEs
"""
import random
import time
from typing import Dict, Any, Literal, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_adapter import DataAdapter, NormalizedData


@dataclass
class AANormalizedData(NormalizedData):
    """Normalized Account Aggregator data structure"""
    
    def __post_init__(self):
        self.source = 'AA'
        if self.data is None:
            self.data = {}


class AAAdapter(DataAdapter):
    """
    Account Aggregator Data Adapter implementation with mock data generation.
    Simulates realistic bank account data with balance and transaction patterns.
    """
    
    def __init__(self):
        """Initialize Account Aggregator adapter"""
        super().__init__()
        self._mock_data_cache: Dict[str, Dict[str, Any]] = {}
    
    def fetch_data(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieves bank account data via Account Aggregator consent token.
        
        Args:
            identifier: Account Aggregator consent token
            
        Returns:
            Raw bank account data dictionary
            
        Raises:
            Exception: If data retrieval fails (5% failure rate in mock mode)
        """
        # Simulate network latency (50-200ms)
        latency_ms = random.randint(50, 200)
        time.sleep(latency_ms / 1000.0)
        
        # Simulate 95% success rate
        if random.random() > 0.95:
            self._update_status(False, "Failed to retrieve AA data: Consent expired")
            raise Exception("Failed to retrieve AA data: Consent expired")
        
        # Return cached data if available, otherwise generate new
        if identifier not in self._mock_data_cache:
            self._mock_data_cache[identifier] = self._generate_mock_data(identifier)
        
        self._update_status(True)
        return self._mock_data_cache[identifier]
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> AANormalizedData:
        """
        Normalizes raw bank account data to standard format.
        
        Args:
            raw_data: Raw AA data from fetch_data()
            
        Returns:
            AANormalizedData object with standardized structure
        """
        account_data = raw_data['account_data']
        transactions = raw_data['transactions']
        
        # Calculate average balance over the period
        balances = [t['balance_after'] for t in transactions]
        average_balance = sum(balances) / len(balances) if balances else account_data['current_balance']
        
        # Find minimum balance
        minimum_balance = min(balances) if balances else account_data['current_balance']
        
        # Calculate credit/debit ratio
        credits = sum(t['amount'] for t in transactions if t['type'] == 'credit')
        debits = sum(t['amount'] for t in transactions if t['type'] == 'debit')
        credit_debit_ratio = credits / debits if debits > 0 else 0
        
        # Calculate liquidity ratio (current balance / average monthly outflow)
        average_monthly_outflow = debits / 6  # Assuming 6 months of data
        liquidity_ratio = account_data['current_balance'] / average_monthly_outflow if average_monthly_outflow > 0 else 1.0
        
        # Count overdraft frequency (times balance went negative)
        overdraft_frequency = sum(1 for b in balances if b < 0)
        
        return AANormalizedData(
            source='AA',
            fetched_at=datetime.now(),
            data={
                'average_balance': average_balance,
                'minimum_balance': minimum_balance,
                'credit_debit_ratio': credit_debit_ratio,
                'liquidity_ratio': liquidity_ratio,
                'overdraft_frequency': overdraft_frequency
            }
        )
    
    def _generate_mock_data(self, consent_token: str) -> Dict[str, Any]:
        """
        Generates realistic mock bank account data with balance and transaction patterns.
        
        Args:
            consent_token: Account Aggregator consent token
            
        Returns:
            Dictionary containing mock bank account data
        """
        # Generate current balance (50K - 5M)
        current_balance = random.uniform(50_000, 5_000_000)
        
        # Generate 6 months of transaction history
        transactions: List[Dict[str, Any]] = []
        balance = current_balance
        
        # Work backwards from current date
        num_transactions = random.randint(100, 500)
        for i in range(num_transactions):
            # Random transaction type (slightly more credits for healthy business)
            transaction_type = 'credit' if random.random() < 0.55 else 'debit'
            
            # Generate transaction amount
            if transaction_type == 'credit':
                amount = random.uniform(5000, 200000)
                balance_after = balance
                balance_before = balance - amount
            else:
                amount = random.uniform(3000, 150000)
                balance_after = balance
                balance_before = balance + amount
            
            # Random timestamp within last 6 months
            days_ago = random.randint(0, 180)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            transactions.append({
                'transaction_id': f'TXN{i:06d}',
                'type': transaction_type,
                'amount': amount,
                'balance_before': balance_before,
                'balance_after': balance_after,
                'timestamp': timestamp,
                'description': f'{"Payment received" if transaction_type == "credit" else "Payment made"}'
            })
            
            # Update balance for next iteration (going backwards)
            balance = balance_before
        
        # Sort transactions by timestamp (oldest first)
        transactions.sort(key=lambda x: x['timestamp'])
        
        # Recalculate balances forward to ensure consistency
        running_balance = transactions[0]['balance_before']
        for t in transactions:
            if t['type'] == 'credit':
                running_balance += t['amount']
            else:
                running_balance -= t['amount']
            t['balance_after'] = running_balance
        
        return {
            'consent_token': consent_token,
            'account_data': {
                'account_number': f'XXXX{random.randint(1000, 9999)}',
                'bank_name': random.choice(['HDFC Bank', 'ICICI Bank', 'Axis Bank', 'SBI', 'Kotak Mahindra']),
                'account_type': 'Current',
                'current_balance': current_balance,
                'currency': 'INR'
            },
            'transactions': transactions
        }
