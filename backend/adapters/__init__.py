"""
Data Adapter Module
Provides adapters for GST, UPI, Account Aggregator, and EPFO data sources
"""
from .base_adapter import DataAdapter, AdapterStatus, NormalizedData
from .gst_adapter import GSTAdapter, GSTNormalizedData
from .upi_adapter import UPIAdapter, UPINormalizedData
from .aa_adapter import AAAdapter, AANormalizedData
from .epfo_adapter import EPFOAdapter, EPFONormalizedData

__all__ = [
    'DataAdapter',
    'AdapterStatus',
    'NormalizedData',
    'GSTAdapter',
    'GSTNormalizedData',
    'UPIAdapter',
    'UPINormalizedData',
    'AAAdapter',
    'AANormalizedData',
    'EPFOAdapter',
    'EPFONormalizedData'
]
