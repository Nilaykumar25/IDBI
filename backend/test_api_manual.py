"""
Manual Integration Tests for REST API Endpoints
Run this to verify all endpoints are properly implemented
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

# Mock JWT token for testing (replace with real token in production)
MOCK_TOKEN = "mock-jwt-token-for-testing"

def test_compute_score():
    """Test POST /api/scores endpoint"""
    print("\n=== Testing POST /api/scores ===")
    
    payload = {
        "msmeId": "TEST-MSME-001",
        "gstNumber": "29ABCDE1234F1Z5",
        "upiId": "test@upi",
        "aaConsentToken": "mock-consent-token",
        "epfoEstablishmentId": "EPFO12345",
        "sector": "Trader"
    }
    
    headers = {
        "Authorization": f"Bearer {MOCK_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scores", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'data' in data
            assert 0 <= data['data']['compositeScore'] <= 100
            print("✓ POST /api/scores works correctly")
        else:
            print("✗ POST /api/scores returned unexpected status")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_retrieve_score():
    """Test GET /api/scores/:msmeId endpoint"""
    print("\n=== Testing GET /api/scores/:msmeId ===")
    
    headers = {
        "Authorization": f"Bearer {MOCK_TOKEN}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/scores/TEST-MSME-001", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 404]:
            print("✓ GET /api/scores/:msmeId works correctly")
        else:
            print("✗ GET /api/scores/:msmeId returned unexpected status")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_retrieve_history():
    """Test GET /api/scores/:msmeId/history endpoint"""
    print("\n=== Testing GET /api/scores/:msmeId/history ===")
    
    headers = {
        "Authorization": f"Bearer {MOCK_TOKEN}"
    }
    
    # Test 1: Default 6 months
    try:
        response = requests.get(f"{BASE_URL}/scores/TEST-MSME-001/history", headers=headers)
        print(f"Status Code (no params): {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ GET /api/scores/:msmeId/history (default range) works")
        else:
            print("✗ Unexpected status for default range")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: With date range
    try:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{BASE_URL}/scores/TEST-MSME-001/history?startDate={start_date}&endDate={end_date}",
            headers=headers
        )
        print(f"\nStatus Code (with date range): {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ GET /api/scores/:msmeId/history (with date range) works")
        else:
            print("✗ Unexpected status for date range")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_simulate():
    """Test POST /api/simulate endpoint"""
    print("\n=== Testing POST /api/simulate ===")
    
    payload = {
        "features": {
            "revenueStability": 0.85,
            "transactionVelocity": 0.78,
            "liquidityRatio": 0.82,
            "employmentConsistency": 0.65,
            "complianceScore": 0.92,
            "growthIndicator": 0.71
        },
        "sector": "Trader"
    }
    
    headers = {
        "Authorization": f"Bearer {MOCK_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/simulate", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 0 <= data['data']['compositeScore'] <= 100
            print("✓ POST /api/simulate works correctly")
        else:
            print("✗ POST /api/simulate returned unexpected status")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_ecosystem_endpoints():
    """Test ecosystem integration endpoints"""
    print("\n=== Testing Ecosystem Endpoints ===")
    
    headers = {
        "Authorization": f"Bearer {MOCK_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test 1: AA consent
    try:
        response = requests.post(f"{BASE_URL}/ecosystem/consent", headers=headers)
        print(f"\nPOST /api/ecosystem/consent - Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ POST /api/ecosystem/consent works")
        else:
            print("✗ Unexpected status")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: ULI publish
    try:
        response = requests.post(f"{BASE_URL}/ecosystem/publish", headers=headers)
        print(f"\nPOST /api/ecosystem/publish - Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ POST /api/ecosystem/publish works")
        else:
            print("✗ Unexpected status")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Lender matching
    for risk_band in ['Low', 'Medium', 'High']:
        try:
            response = requests.get(
                f"{BASE_URL}/ecosystem/lenders?riskBand={risk_band}",
                headers=headers
            )
            print(f"\nGET /api/ecosystem/lenders?riskBand={risk_band} - Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print(f"✓ GET /api/ecosystem/lenders (risk={risk_band}) works")
            else:
                print(f"✗ Unexpected status for risk={risk_band}")
        except Exception as e:
            print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("MSME Financial Health Score API - Manual Tests")
    print("=" * 60)
    print("\nNOTE: Make sure the Flask server is running on http://localhost:5000")
    print("      Start it with: python app.py")
    print("\nNOTE: These tests will fail with 401 if authentication is enabled")
    print("      You may need to temporarily disable @require_auth for testing")
    
    input("\nPress Enter to continue...")
    
    test_compute_score()
    test_retrieve_score()
    test_retrieve_history()
    test_simulate()
    test_ecosystem_endpoints()
    
    print("\n" + "=" * 60)
    print("Manual testing complete!")
    print("=" * 60)
