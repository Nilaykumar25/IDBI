"""
Test script for data adapters
Verifies all adapters can fetch and normalize data correctly
"""
import sys
import traceback
from adapters import (
    GSTAdapter, UPIAdapter, AAAdapter, EPFOAdapter
)


def test_adapter(adapter_name, adapter_instance, test_identifier):
    """Test a single adapter"""
    print(f"\n{'='*60}")
    print(f"Testing {adapter_name}")
    print('='*60)
    
    try:
        # Test fetch_data
        print(f"  Fetching data with identifier: {test_identifier}")
        raw_data = adapter_instance.fetch_data(test_identifier)
        print(f"  ✓ fetch_data() succeeded")
        
        # Test normalize_data
        print(f"  Normalizing data...")
        normalized_data = adapter_instance.normalize_data(raw_data)
        print(f"  ✓ normalize_data() succeeded")
        
        # Display normalized data
        print(f"\n  Normalized Data:")
        print(f"    Source: {normalized_data.source}")
        print(f"    Fetched At: {normalized_data.fetched_at}")
        print(f"    Data:")
        for key, value in normalized_data.data.items():
            if isinstance(value, float):
                print(f"      {key}: {value:.4f}")
            else:
                print(f"      {key}: {value}")
        
        # Test get_status
        status = adapter_instance.get_status()
        print(f"\n  Adapter Status:")
        print(f"    Healthy: {status.is_healthy}")
        print(f"    Last Fetch: {status.last_fetch_timestamp}")
        print(f"    Error: {status.error_message}")
        
        print(f"\n  ✅ {adapter_name} test PASSED")
        return True
        
    except Exception as e:
        print(f"\n  ❌ {adapter_name} test FAILED")
        print(f"  Error: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """Run all adapter tests"""
    print("\n" + "="*60)
    print("Data Adapter Test Suite")
    print("="*60)
    
    results = []
    
    # Test GST Adapter
    gst_adapter = GSTAdapter()
    results.append(test_adapter("GSTAdapter", gst_adapter, "29ABCDE1234F1Z5"))
    
    # Test UPI Adapter
    upi_adapter = UPIAdapter()
    results.append(test_adapter("UPIAdapter", upi_adapter, "business@okaxis"))
    
    # Test AA Adapter
    aa_adapter = AAAdapter()
    results.append(test_adapter("AAAdapter", aa_adapter, "consent-token-abc123"))
    
    # Test EPFO Adapter
    epfo_adapter = EPFOAdapter()
    results.append(test_adapter("EPFOAdapter", epfo_adapter, "EPFO12345"))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n  ✅ All adapter tests PASSED!")
        return 0
    else:
        print("\n  ❌ Some adapter tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
