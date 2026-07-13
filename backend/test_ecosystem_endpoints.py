"""
Simple integration test for ecosystem endpoints
Tests the three ecosystem integration API endpoints
"""
import os
import sys

# Set TEST_MODE before importing app
os.environ['TEST_MODE'] = 'true'
os.environ['ADAPTER_MODE'] = 'mock'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json


def test_ecosystem_endpoints():
    """Test all three ecosystem endpoints"""
    
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Auth header for test mode (test middleware accepts any token)
    headers = {'Authorization': 'Bearer test-token-123'}
    
    print("Testing Ecosystem Integration Endpoints")
    print("=" * 50)
    
    # Test 1: POST /api/ecosystem/consent
    print("\n1. Testing POST /api/ecosystem/consent")
    response = client.post('/api/ecosystem/consent', headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert data['success'] is True, "Expected success=True"
    assert 'consentToken' in data['data'], "Missing consentToken"
    assert 'mock-consent-' in data['data']['consentToken'], "Invalid consent token format"
    assert data['data']['status'] == 'approved', "Expected status=approved"
    assert 'timestamp' in data['data'], "Missing timestamp"
    print(f"   ✓ Consent token: {data['data']['consentToken'][:30]}...")
    print(f"   ✓ Status: {data['data']['status']}")
    print(f"   ✓ Timestamp: {data['data']['timestamp']}")
    
    # Test 2: POST /api/ecosystem/publish
    print("\n2. Testing POST /api/ecosystem/publish")
    response = client.post('/api/ecosystem/publish', headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert data['success'] is True, "Expected success=True"
    assert 'transactionId' in data['data'], "Missing transactionId"
    assert 'uli-txn-' in data['data']['transactionId'], "Invalid transaction ID format"
    assert data['data']['status'] == 'published', "Expected status=published"
    assert 'message' in data['data'], "Missing message"
    assert 'timestamp' in data['data'], "Missing timestamp"
    print(f"   ✓ Transaction ID: {data['data']['transactionId'][:30]}...")
    print(f"   ✓ Status: {data['data']['status']}")
    print(f"   ✓ Message: {data['data']['message']}")
    print(f"   ✓ Timestamp: {data['data']['timestamp']}")
    
    # Test 3: GET /api/ecosystem/lenders for each risk band
    risk_bands = ['Low', 'Medium', 'High']
    expected_lender_counts = {'Low': 3, 'Medium': 2, 'High': 2}
    
    for risk_band in risk_bands:
        print(f"\n3. Testing GET /api/ecosystem/lenders?riskBand={risk_band}")
        response = client.get(f'/api/ecosystem/lenders?riskBand={risk_band}', headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] is True, "Expected success=True"
        assert data['data']['riskBand'] == risk_band, f"Expected riskBand={risk_band}"
        
        lenders = data['data']['lenders']
        assert len(lenders) >= 2, f"Expected at least 2 lenders, got {len(lenders)}"
        assert len(lenders) == expected_lender_counts[risk_band], f"Expected {expected_lender_counts[risk_band]} lenders"
        
        print(f"   ✓ Risk Band: {risk_band}")
        print(f"   ✓ Number of lenders: {len(lenders)}")
        
        for idx, lender in enumerate(lenders, 1):
            assert 'name' in lender, "Missing lender name"
            assert 'productType' in lender, "Missing product type"
            assert 'interestRate' in lender, "Missing interest rate"
            assert 'maxAmount' in lender, "Missing max amount"
            
            print(f"   ✓ Lender {idx}: {lender['name']}")
            print(f"     - Product: {lender['productType']}")
            print(f"     - Rate: {lender['interestRate']}")
            print(f"     - Max Amount: {lender['maxAmount']}")
    
    # Test 4: GET /api/ecosystem/lenders without riskBand (should fail)
    print("\n4. Testing GET /api/ecosystem/lenders without riskBand (negative test)")
    response = client.get('/api/ecosystem/lenders', headers=headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = json.loads(response.data)
    assert data['success'] is False, "Expected success=False"
    assert 'error' in data, "Missing error message"
    print(f"   ✓ Correctly returned 400 with error: {data['error']}")
    
    # Test 5: GET /api/ecosystem/lenders with invalid riskBand (should fail)
    print("\n5. Testing GET /api/ecosystem/lenders with invalid riskBand (negative test)")
    response = client.get('/api/ecosystem/lenders?riskBand=Invalid', headers=headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = json.loads(response.data)
    assert data['success'] is False, "Expected success=False"
    assert 'error' in data, "Missing error message"
    print(f"   ✓ Correctly returned 400 with error: {data['error']}")
    
    print("\n" + "=" * 50)
    print("✓ All ecosystem endpoint tests passed!")
    print("=" * 50)


if __name__ == '__main__':
    test_ecosystem_endpoints()
