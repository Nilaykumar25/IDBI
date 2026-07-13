"""
Base Data Adapter Interface and Abstract Class
Provides common structure and methods for all data adapters (GST, UPI, AA, EPFO)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from dataclasses import dataclass


@dataclass
class AdapterStatus:
    """Status information for a data adapter"""
    is_healthy: bool
    last_fetch_timestamp: Optional[datetime]
    error_message: Optional[str]


@dataclass
class NormalizedData:
    """Base class for normalized data from adapters"""
    source: Literal['GST', 'UPI', 'AA', 'EPFO']
    fetched_at: datetime
    data: Dict[str, Any]


class DataAdapter(ABC):
    """
    Abstract base class for all data adapters.
    Defines the interface that all concrete adapters must implement.
    """
    
    def __init__(self):
        """Initialize adapter with default state"""
        self._mode: Literal['mock', 'production'] = 'mock'
        self._status = AdapterStatus(
            is_healthy=True,
            last_fetch_timestamp=None,
            error_message=None
        )
    
    @abstractmethod
    def fetch_data(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieves raw data from external source.
        
        Args:
            identifier: The identifier for the data source (e.g., GST number, UPI ID)
            
        Returns:
            Raw data from the external source as a dictionary
            
        Raises:
            Exception: If data retrieval fails
        """
        pass
    
    @abstractmethod
    def normalize_data(self, raw_data: Dict[str, Any]) -> NormalizedData:
        """
        Normalizes raw data to standard format.
        
        Args:
            raw_data: Raw data from fetch_data()
            
        Returns:
            NormalizedData object with standardized structure
        """
        pass
    
    def set_mode(self, mode: Literal['mock', 'production']) -> None:
        """
        Sets adapter to mock or production mode.
        
        Args:
            mode: 'mock' for simulated data, 'production' for real API calls
        """
        self._mode = mode
    
    def get_status(self) -> AdapterStatus:
        """
        Returns adapter status and last fetch timestamp.
        
        Returns:
            AdapterStatus object with current health information
        """
        return self._status
    
    def _update_status(self, is_healthy: bool, error_message: Optional[str] = None) -> None:
        """
        Internal method to update adapter status.
        
        Args:
            is_healthy: Whether the adapter is functioning correctly
            error_message: Error description if not healthy
        """
        self._status = AdapterStatus(
            is_healthy=is_healthy,
            last_fetch_timestamp=datetime.now() if is_healthy else self._status.last_fetch_timestamp,
            error_message=error_message
        )
