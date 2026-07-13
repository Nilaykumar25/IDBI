"""
Test adapter mode switching (mock/production)
Verifies set_mode() functionality
"""
import sys
from adapters import GSTAdapter, UPIAdapter, AAAdapter, EPFOAdapter


def test_mode_switching(adapter_name, adapter_instance):
    """Test mode switching functionality"""
    print(f"\nTesting {adapter_name} mode switching:")
    
    # Check initial mode (should be mock by default)
    print(f"  Initial mode: {adapter_instance._mode}")
    assert adapter_instance._mode == 'mock', "Default mode should be 'mock'"
    print(f"  ✓ Default mode is 'mock'")
    
    # Switch to production mode
    adapter_instance.set_mode('production')
    print(f"  After set_mode('production'): {adapter_instance._mode}")
    assert adapter_instance._mode == 'production', "Mode should be 'production'"
    print(f"  ✓ Mode switched to 'production'")
    
    # Switch back to mock mode
    adapter_instance.set_mode('mock')
    print(f"  After set_mode('mock'): {adapter_instance._mode}")
    assert adapter_instance._mode == 'mock', "Mode should be 'mock'"
    print(f"  ✓ Mode switched back to 'mock'")
    
    return True


def main():
    """Test mode switching for all adapters"""
    print("="*60)
    print("Adapter Mode Switching Test")
    print("="*60)
    
    results = []
    
    # Test all adapters
    adapters = [
        ("GSTAdapter", GSTAdapter()),
        ("UPIAdapter", UPIAdapter()),
        ("AAAdapter", AAAdapter()),
        ("EPFOAdapter", EPFOAdapter())
    ]
    
    for name, adapter in adapters:
        try:
            result = test_mode_switching(name, adapter)
            results.append(result)
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    
    if all(results):
        print(f"\n  ✅ All mode switching tests PASSED!")
        return 0
    else:
        print(f"\n  ❌ Some mode switching tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
