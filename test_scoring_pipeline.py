#!/usr/bin/env python3
"""
Test script to verify end-to-end scoring pipeline
Tests: Model → API → Supabase persistence
"""
import requests
import json
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

# Configuration
API_BASE_URL = 'http://localhost:5000/api'
TEST_MSME_ID = 'MSME-2024-TEST-001'

# Test data
test_payload = {
    'msmeId': TEST_MSME_ID,
    'gstNumber': '29ABCDE1234F1Z5',
    'upiId': 'business@bank',
    'aaConsentToken': 'AA-CONSENT-TEST123',
    'epfoEstablishmentId': 'EPFO-EST-12345',
    'sector': 'Trader'
}

print("=" * 80)
print("STEP 4: END-TO-END SCORING PIPELINE TEST")
print("=" * 80)

# Step 1: Get auth token (using test mode)
print("\n[1] Getting authentication token...")
try:
    # For test mode, we can use a dummy token
    # In production, you'd need to authenticate with Supabase
    auth_token = "dummy-token-for-test-mode"
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    print("✓ Auth token ready")
except Exception as e:
    print(f"✗ Failed to get auth token: {e}")
    exit(1)

# Step 2: Submit score computation request
print(f"\n[2] Submitting score computation for {TEST_MSME_ID}...")
try:
    response = requests.post(
        f'{API_BASE_URL}/scores',
        json=test_payload,
        headers=headers,
        timeout=10
    )
    
    print(f"Response Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✗ API request failed: {response.text}")
        exit(1)
    
    api_response = response.json()
    
    if not api_response.get('success'):
        print(f"✗ API returned error: {api_response.get('error')}")
        exit(1)
    
    score_data = api_response['data']
    
    print("\n✓ API Response:")
    print(f"  MSME ID: {score_data['msmeId']}")
    print(f"  Composite Score: {score_data['compositeScore']}")
    print(f"  Risk Band: {score_data['riskBand']}")
    print(f"  Confidence Scores:")
    print(f"    Low: {score_data['confidence']['low']}")
    print(f"    Medium: {score_data['confidence']['medium']}")
    print(f"    High: {score_data['confidence']['high']}")
    print(f"  Features (sample):")
    for key, value in list(score_data['features'].items())[:3]:
        print(f"    {key}: {value}")
    print(f"  SHAP Values (sample):")
    for key, value in list(score_data['shapValues'].items())[:3]:
        print(f"    {key}: {value}")
    
    # Save full response for comparison
    full_api_response = score_data
    
except Exception as e:
    print(f"✗ API request failed: {e}")
    exit(1)

# Step 3: Query Supabase directly
print(f"\n[3] Querying Supabase for MSME ID: {TEST_MSME_ID}...")
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("✗ SUPABASE_URL or SUPABASE_KEY not found in environment")
        exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    result = supabase.table('score_history') \
        .select('*') \
        .eq('msme_id', TEST_MSME_ID) \
        .order('computed_at', desc=True) \
        .limit(1) \
        .execute()
    
    if not result.data or len(result.data) == 0:
        print(f"✗ No record found in Supabase for {TEST_MSME_ID}")
        exit(1)
    
    db_record = result.data[0]
    
    print("\n✓ Supabase Record Found:")
    print(f"  ID: {db_record['id']}")
    print(f"  MSME ID: {db_record['msme_id']}")
    print(f"  Composite Score: {db_record['composite_score']}")
    print(f"  Risk Band: {db_record['risk_band']}")
    print(f"  ML Confidence Low: {db_record['ml_confidence_low']}")
    print(f"  ML Confidence Medium: {db_record['ml_confidence_medium']}")
    print(f"  ML Confidence High: {db_record['ml_confidence_high']}")
    print(f"  Features (JSONB): {json.dumps(db_record['features'], indent=4)}")
    print(f"  SHAP Values (JSONB): {json.dumps(db_record['shap_values'], indent=4)}")
    print(f"  Missing Sources: {db_record['missing_sources']}")
    print(f"  Sector: {db_record['sector']}")
    print(f"  Computed At: {db_record['computed_at']}")
    
except Exception as e:
    print(f"✗ Supabase query failed: {e}")
    exit(1)

# Step 4: Validate field consistency
print("\n[4] Validating API Response vs Supabase Record...")
issues_found = []

# Check composite_score
if full_api_response['compositeScore'] != float(db_record['composite_score']):
    issues_found.append(f"Composite score mismatch: API={full_api_response['compositeScore']}, DB={db_record['composite_score']}")

# Check risk_band
if full_api_response['riskBand'] != db_record['risk_band']:
    issues_found.append(f"Risk band mismatch: API={full_api_response['riskBand']}, DB={db_record['risk_band']}")

# Check confidence scores
if full_api_response['confidence']['low'] != float(db_record['ml_confidence_low']):
    issues_found.append(f"Confidence low mismatch: API={full_api_response['confidence']['low']}, DB={db_record['ml_confidence_low']}")

if full_api_response['confidence']['medium'] != float(db_record['ml_confidence_medium']):
    issues_found.append(f"Confidence medium mismatch: API={full_api_response['confidence']['medium']}, DB={db_record['ml_confidence_medium']}")

if full_api_response['confidence']['high'] != float(db_record['ml_confidence_high']):
    issues_found.append(f"Confidence high mismatch: API={full_api_response['confidence']['high']}, DB={db_record['ml_confidence_high']}")

# Check features - KEY CHECK
print("\n  Checking features JSONB structure...")
api_features = full_api_response['features']
db_features = db_record['features']

print(f"    API features keys: {list(api_features.keys())}")
print(f"    DB features keys: {list(db_features.keys())}")

if set(api_features.keys()) != set(db_features.keys()):
    issues_found.append(f"Features keys mismatch! API uses: {list(api_features.keys())}, DB has: {list(db_features.keys())}")

# Check SHAP values
print("\n  Checking SHAP values JSONB structure...")
api_shap = full_api_response['shapValues']
db_shap = db_record['shap_values']

print(f"    API SHAP keys: {list(api_shap.keys())}")
print(f"    DB SHAP keys: {list(db_shap.keys())}")

if set(api_shap.keys()) != set(db_shap.keys()):
    issues_found.append(f"SHAP keys mismatch! API uses: {list(api_shap.keys())}, DB has: {list(db_shap.keys())}")

# Report results
print("\n" + "=" * 80)
if issues_found:
    print("❌ VALIDATION FAILED - Issues Found:")
    for issue in issues_found:
        print(f"  ✗ {issue}")
else:
    print("✅ VALIDATION PASSED - All fields match between API and Supabase!")

print("=" * 80)
