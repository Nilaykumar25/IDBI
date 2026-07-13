"""
EPFO Data Adapter
Retrieves and normalizes EPFO (Employees' Provident Fund Organisation) data for MSMEs
"""
import random
import time
from typing import Dict, Any, Literal, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_adapter import DataAdapter, NormalizedData


@dataclass
class EPFONormalizedData(NormalizedData):
    """Normalized EPFO data structure"""
    
    def __post_init__(self):
        self.source = 'EPFO'
        if self.data is None:
            self.data = {}


class EPFOAdapter(DataAdapter):
    """
    EPFO Data Adapter implementation with mock data generation.
    Simulates realistic employee and contribution data.
    """
    
    def __init__(self):
        """Initialize EPFO adapter"""
        super().__init__()
        self._mock_data_cache: Dict[str, Dict[str, Any]] = {}
    
    def fetch_data(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieves EPFO employee and contribution data via establishment ID.
        
        Args:
            identifier: EPFO establishment ID
            
        Returns:
            Raw EPFO data dictionary
            
        Raises:
            Exception: If data retrieval fails (5% failure rate in mock mode)
        """
        # Simulate network latency (50-200ms)
        latency_ms = random.randint(50, 200)
        time.sleep(latency_ms / 1000.0)
        
        # Simulate 95% success rate
        if random.random() > 0.95:
            self._update_status(False, "Failed to retrieve EPFO data: Service unavailable")
            raise Exception("Failed to retrieve EPFO data: Service unavailable")
        
        # Return cached data if available, otherwise generate new
        if identifier not in self._mock_data_cache:
            self._mock_data_cache[identifier] = self._generate_mock_data(identifier)
        
        self._update_status(True)
        return self._mock_data_cache[identifier]
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> EPFONormalizedData:
        """
        Normalizes raw EPFO data to standard format.
        
        Args:
            raw_data: Raw EPFO data from fetch_data()
            
        Returns:
            EPFONormalizedData object with standardized structure
        """
        # Current employee count
        employee_count = raw_data['current_employee_count']
        
        # Calculate monthly contribution amount (latest month)
        latest_contributions = raw_data['monthly_contributions'][-1]
        monthly_contribution_amount = latest_contributions['total_amount']
        
        # Calculate contribution regularity (paid / expected over last 12 months)
        total_paid = sum(1 for c in raw_data['monthly_contributions'] if c['paid'])
        expected_contributions = len(raw_data['monthly_contributions'])
        contribution_regularity = total_paid / expected_contributions if expected_contributions > 0 else 0
        
        # Calculate employee growth rate (quarter-over-quarter)
        # Compare last 3 months vs previous 3 months
        recent_quarter_counts = [c['employee_count'] for c in raw_data['monthly_contributions'][-3:]]
        previous_quarter_counts = [c['employee_count'] for c in raw_data['monthly_contributions'][-6:-3]]
        
        recent_avg = sum(recent_quarter_counts) / len(recent_quarter_counts) if recent_quarter_counts else employee_count
        previous_avg = sum(previous_quarter_counts) / len(previous_quarter_counts) if previous_quarter_counts else employee_count
        
        employee_growth_rate = ((recent_avg / previous_avg) - 1) * 100 if previous_avg > 0 else 0
        
        # Calculate average wage per employee (from latest contribution)
        average_wage_per_employee = monthly_contribution_amount / employee_count if employee_count > 0 else 0
        
        return EPFONormalizedData(
            source='EPFO',
            fetched_at=datetime.now(),
            data={
                'employee_count': employee_count,
                'monthly_contribution_amount': monthly_contribution_amount,
                'contribution_regularity': contribution_regularity,
                'employee_growth_rate': employee_growth_rate,
                'average_wage_per_employee': average_wage_per_employee
            }
        )
    
    def _generate_mock_data(self, establishment_id: str) -> Dict[str, Any]:
        """
        Generates realistic mock EPFO data with employee and contribution patterns.
        
        Args:
            establishment_id: EPFO establishment ID
            
        Returns:
            Dictionary containing mock EPFO employee and contribution data
        """
        # Generate current employee count (5-100 employees for MSME)
        current_employee_count = random.randint(5, 100)
        
        # Generate 12 months of contribution history
        monthly_contributions: List[Dict[str, Any]] = []
        
        # Start with slightly lower employee count 12 months ago
        employee_count_12_months_ago = int(current_employee_count * random.uniform(0.7, 1.0))
        
        for month_offset in range(12):
            # Gradually change employee count towards current count
            progress = month_offset / 11
            employee_count = int(
                employee_count_12_months_ago + 
                (current_employee_count - employee_count_12_months_ago) * progress
            )
            
            # Add some random fluctuation
            employee_count = max(1, employee_count + random.randint(-2, 2))
            
            # Generate average wage per employee (₹8,000 - ₹25,000 per month)
            avg_wage = random.uniform(8000, 25000)
            
            # EPF contribution is typically 12% of basic salary (employer + employee)
            # We'll use wage as proxy for basic salary
            total_contribution = employee_count * avg_wage * 0.12
            
            # Determine if contribution was paid (simulate regularity)
            # Most months should be paid, some might be missed
            contribution_paid = random.random() < 0.90  # 90% payment rate
            
            # Generate timestamp for this month
            months_ago = 11 - month_offset
            contribution_date = datetime.now() - timedelta(days=months_ago * 30)
            
            monthly_contributions.append({
                'month': contribution_date.strftime('%Y-%m'),
                'employee_count': employee_count,
                'total_amount': total_contribution if contribution_paid else 0,
                'paid': contribution_paid,
                'due_date': contribution_date,
                'payment_date': contribution_date + timedelta(days=random.randint(1, 15)) if contribution_paid else None
            })
        
        return {
            'establishment_id': establishment_id,
            'current_employee_count': current_employee_count,
            'monthly_contributions': monthly_contributions,
            'establishment_name': f'MSME Establishment {establishment_id[-6:]}',
            'registration_date': datetime.now() - timedelta(days=random.randint(365, 3650))
        }
