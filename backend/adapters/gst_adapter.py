"""
GST Data Adapter
Retrieves and normalizes GST (Goods and Services Tax) data for MSMEs
"""
import random
import time
from typing import Dict, Any, Literal, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_adapter import DataAdapter, NormalizedData


@dataclass
class GSTNormalizedData(NormalizedData):
    """Normalized GST data structure"""
    
    def __post_init__(self):
        self.source = 'GST'
        if self.data is None:
            self.data = {}


class GSTAdapter(DataAdapter):
    """
    GST Data Adapter implementation with mock data generation.
    Simulates realistic GST revenue patterns with latency and variability.
    """
    
    def __init__(self):
        """Initialize GST adapter"""
        super().__init__()
        self._mock_data_cache: Dict[str, Dict[str, Any]] = {}
    
    def fetch_data(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieves GST data for the given GST number.
        
        Args:
            identifier: GST identification number
            
        Returns:
            Raw GST data dictionary
            
        Raises:
            Exception: If data retrieval fails (5% failure rate in mock mode)
        """
        # Simulate network latency (50-200ms)
        latency_ms = random.randint(50, 200)
        time.sleep(latency_ms / 1000.0)
        
        # Simulate 95% success rate
        if random.random() > 0.95:
            self._update_status(False, "Failed to retrieve GST data: Connection timeout")
            raise Exception("Failed to retrieve GST data: Connection timeout")
        
        # Return cached data if available, otherwise generate new
        if identifier not in self._mock_data_cache:
            self._mock_data_cache[identifier] = self._generate_mock_data(identifier)
        
        self._update_status(True)
        return self._mock_data_cache[identifier]
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> GSTNormalizedData:
        """
        Normalizes raw GST data to standard format.
        
        Args:
            raw_data: Raw GST data from fetch_data()
            
        Returns:
            GSTNormalizedData object with standardized structure
        """
        monthly_revenue = raw_data['monthly_revenue']
        annual_revenue = sum(monthly_revenue)
        avg_revenue = annual_revenue / len(monthly_revenue)
        
        # Calculate standard deviation for revenue stability
        variance = sum((x - avg_revenue) ** 2 for x in monthly_revenue) / len(monthly_revenue)
        std_dev = variance ** 0.5
        
        # Calculate year-over-year growth rate
        first_quarter_avg = sum(monthly_revenue[:3]) / 3
        last_quarter_avg = sum(monthly_revenue[-3:]) / 3
        revenue_growth_rate = ((last_quarter_avg / first_quarter_avg) - 1) * 100 if first_quarter_avg > 0 else 0
        
        return GSTNormalizedData(
            source='GST',
            fetched_at=datetime.now(),
            data={
                'annual_revenue': annual_revenue,
                'filing_frequency': raw_data['filed_returns'] / raw_data['expected_returns'],
                'compliance_status': raw_data['compliance_status'],
                'revenue_growth_rate': revenue_growth_rate,
                'last_filing_date': raw_data['last_filing_date']
            }
        )
    
    def _generate_mock_data(self, gst_number: str) -> Dict[str, Any]:
        """
        Generates realistic mock GST data with revenue patterns.
        
        Args:
            gst_number: GST identification number
            
        Returns:
            Dictionary containing mock GST data
        """
        # Generate base annual revenue between 1M and 50M
        base_revenue = random.uniform(1_000_000, 50_000_000)
        
        # Generate 12 months of revenue with realistic variability
        monthly_revenue: List[float] = []
        for month in range(12):
            # Add seasonal variation and random fluctuation
            seasonal_factor = 1 + (0.2 * random.uniform(-1, 1))
            monthly_value = (base_revenue / 12) * seasonal_factor
            monthly_revenue.append(monthly_value)
        
        # Generate filing compliance data
        expected_returns = 12
        filed_returns = random.randint(8, 12)
        
        # Determine compliance status based on filing frequency
        if filed_returns >= 11:
            compliance_status = 'compliant'
        elif filed_returns >= 9:
            compliance_status = 'partial'
        else:
            compliance_status = 'non-compliant'
        
        # Generate last filing date (within last 30 days)
        days_ago = random.randint(1, 30)
        last_filing_date = datetime.now() - timedelta(days=days_ago)
        
        return {
            'gst_number': gst_number,
            'monthly_revenue': monthly_revenue,
            'filed_returns': filed_returns,
            'expected_returns': expected_returns,
            'compliance_status': compliance_status,
            'last_filing_date': last_filing_date
        }
