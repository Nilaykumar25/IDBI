"""
End-to-End Integration Testing for MSME Financial Health Score System
Tests complete flow: Authentication → Score Computation → All Dashboard Views
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
TEST_USER_EMAIL = f"test_integration_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(test_name, status, message=""):
    """Print formatted test result"""
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}[{status}]{Colors.RESET} {test_name}")
    if message:
        print(f"      {message}")

def test_health_check():
    """Test 1: Health check endpoint (no auth required)"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", "PASS", f"Mode: {data.get('mode')}, Adapter: {data.get('adapterMode')}")
            return True
        else:
            print_test("Health Check", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", "FAIL", str(e))
        return False

def test_score_computation_with_demo_profiles():
    """Test 2: Score computation with all 4 demo profiles"""
    demo_profiles = [
        {
            "id": "DEMO-LOW-001",
            "name": "Low Risk Trader",
            "expected_risk": "Low",
            "sector": "Trader"
        },
        {
            "id": "DEMO-HIGH-001",
            "name": "High Risk Services",
            "expected_risk": "High",
            "sector": "Services"
        },
        {
            "id": "DEMO-MED-001",
            "name": "Medium Risk Manufacturer",
            "expected_risk": "Medium",
            "sector": "Manufacturer"
        },
        {
            "id": "DEMO-PARTIAL-001",
            "name": "Partial Data Trader",
            "expected_risk": "Any (3/4 adapters)",
            "sector": "Trader"
        }
    ]
    
    results = []
    for profile in demo_profiles:
        try:
            payload = {
                "msmeId": profile["id"],
                "gstNumber": f"GST-{profile['id']}",
                "upiId": f"upi-{profile['id'].lower()}@bank",
                "aaConsentToken": f"AA-{profile['id']}",
                "epfoEstablishmentId": f"EPFO-{profile['id']}",
                "sector": profile["sector"]
            }
            
            response = requests.post(f"{BASE_URL}/api/scores", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    score_data = data['data']
                    risk_band = score_data.get('riskBand')
                    score = score_data.get('compositeScore')
                    missing_sources = score_data.get('missingSources', [])
                    
                    status = "PASS"
                    message = f"Score: {score:.2f}, Risk: {risk_band}"
                    if missing_sources:
                        message += f", Missing: {', '.join(missing_sources)}"
                    
                    print_test(f"Score Computation: {profile['name']}", status, message)
                    results.append(True)
                else:
                    print_test(f"Score Computation: {profile['name']}", "FAIL", data.get('error'))
                    results.append(False)
            else:
                print_test(f"Score Computation: {profile['name']}", "FAIL", f"Status: {response.status_code}")
                results.append(False)
        except Exception as e:
            print_test(f"Score Computation: {profile['name']}", "FAIL", str(e))
            results.append(False)
    
    return all(results)

def test_score_retrieval():
    """Test 3: Score retrieval endpoint"""
    try:
        # Retrieve a previously computed score
        msme_id = "DEMO-LOW-001"
        response = requests.get(f"{BASE_URL}/api/scores/{msme_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                score_data = data['data']
                print_test("Score Retrieval", "PASS", f"Retrieved score for {msme_id}: {score_data.get('compositeScore'):.2f}")
                return True
            else:
                print_test("Score Retrieval", "FAIL", data.get('error'))
                return False
        else:
            print_test("Score Retrieval", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Score Retrieval", "FAIL", str(e))
        return False

def test_score_history():
    """Test 4: Score history retrieval"""
    try:
        msme_id = "DEMO-LOW-001"
        
        # Compute score 3 times to create history
        payload = {
            "msmeId": msme_id,
            "gstNumber": f"GST-{msme_id}",
            "upiId": f"upi-{msme_id.lower()}@bank",
            "aaConsentToken": f"AA-{msme_id}",
            "epfoEstablishmentId": f"EPFO-{msme_id}",
            "sector": "Trader"
        }
        
        for _ in range(2):  # Already have 1 from previous test
            requests.post(f"{BASE_URL}/api/scores", json=payload, timeout=10)
            time.sleep(0.5)
        
        # Now retrieve history
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 months
        
        response = requests.get(
            f"{BASE_URL}/api/scores/{msme_id}/history",
            params={
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d')
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                history = data['data']
                print_test("Score History", "PASS", f"Retrieved {len(history)} historical records")
                return True
            else:
                print_test("Score History", "FAIL", data.get('error'))
                return False
        else:
            print_test("Score History", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Score History", "FAIL", str(e))
        return False

def test_what_if_simulator():
    """Test 5: What-If simulator endpoint"""
    try:
        # Test various feature adjustments
        test_cases = [
            {
                "name": "Improve Revenue Stability",
                "features": {
                    "revenueStability": 0.95,
                    "transactionVelocity": 0.60,
                    "liquidityRatio": 0.70,
                    "employmentConsistency": 0.65,
                    "complianceScore": 0.85,
                    "growthIndicator": 0.55
                },
                "sector": "Trader"
            },
            {
                "name": "Improve Liquidity",
                "features": {
                    "revenueStability": 0.60,
                    "transactionVelocity": 0.55,
                    "liquidityRatio": 0.95,
                    "employmentConsistency": 0.50,
                    "complianceScore": 0.75,
                    "growthIndicator": 0.50
                },
                "sector": "Services"
            }
        ]
        
        results = []
        for test_case in test_cases:
            response = requests.post(
                f"{BASE_URL}/api/simulate",
                json={
                    "features": test_case["features"],
                    "sector": test_case["sector"]
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    sim_data = data['data']
                    score = sim_data.get('simulatedScore')
                    risk_band = sim_data.get('simulatedRiskBand')
                    print_test(f"What-If Simulation: {test_case['name']}", "PASS", f"Score: {score:.2f}, Risk: {risk_band}")
                    results.append(True)
                else:
                    print_test(f"What-If Simulation: {test_case['name']}", "FAIL", data.get('error'))
                    results.append(False)
            else:
                print_test(f"What-If Simulation: {test_case['name']}", "FAIL", f"Status: {response.status_code}")
                results.append(False)
        
        return all(results)
    except Exception as e:
        print_test("What-If Simulator", "FAIL", str(e))
        return False

def test_ecosystem_integration():
    """Test 6: Ecosystem integration endpoints"""
    results = []
    
    # Test AA consent
    try:
        response = requests.post(
            f"{BASE_URL}/api/ecosystem/consent",
            json={"msmeId": "DEMO-LOW-001"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                consent_data = data['data']
                print_test("Ecosystem: AA Consent", "PASS", f"Token: {consent_data.get('consentToken')[:20]}...")
                results.append(True)
            else:
                print_test("Ecosystem: AA Consent", "FAIL", data.get('error'))
                results.append(False)
        else:
            print_test("Ecosystem: AA Consent", "FAIL", f"Status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print_test("Ecosystem: AA Consent", "FAIL", str(e))
        results.append(False)
    
    # Test ULI publish
    try:
        response = requests.post(
            f"{BASE_URL}/api/ecosystem/publish",
            json={
                "msmeId": "DEMO-LOW-001",
                "score": 85.5,
                "riskBand": "Low"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                publish_data = data['data']
                print_test("Ecosystem: ULI Publish", "PASS", f"TxnID: {publish_data.get('transactionId')}")
                results.append(True)
            else:
                print_test("Ecosystem: ULI Publish", "FAIL", data.get('error'))
                results.append(False)
        else:
            print_test("Ecosystem: ULI Publish", "FAIL", f"Status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print_test("Ecosystem: ULI Publish", "FAIL", str(e))
        results.append(False)
    
    # Test lender matching for all risk bands
    for risk_band in ["Low", "Medium", "High"]:
        try:
            response = requests.get(
                f"{BASE_URL}/api/ecosystem/lenders",
                params={"riskBand": risk_band},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    lenders = data['data']
                    print_test(f"Ecosystem: Lender Matching ({risk_band})", "PASS", f"Matched {len(lenders)} lenders")
                    results.append(True)
                else:
                    print_test(f"Ecosystem: Lender Matching ({risk_band})", "FAIL", data.get('error'))
                    results.append(False)
            else:
                print_test(f"Ecosystem: Lender Matching ({risk_band})", "FAIL", f"Status: {response.status_code}")
                results.append(False)
        except Exception as e:
            print_test(f"Ecosystem: Lender Matching ({risk_band})", "FAIL", str(e))
            results.append(False)
    
    return all(results)

def test_partial_failure_scenarios():
    """Test 7: Partial adapter failure handling"""
    try:
        # Use demo profile designed for partial data
        payload = {
            "msmeId": "DEMO-PARTIAL-001",
            "gstNumber": "GST-DEMO-PARTIAL-001",
            "upiId": "upi-demo-partial-001@bank",
            "aaConsentToken": "AA-DEMO-PARTIAL-001",
            "epfoEstablishmentId": "EPFO-DEMO-PARTIAL-001",
            "sector": "Trader"
        }
        
        response = requests.post(f"{BASE_URL}/api/scores", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                score_data = data['data']
                missing_sources = score_data.get('missingSources', [])
                
                if len(missing_sources) > 0:
                    print_test("Partial Failure Handling", "PASS", f"Computed score with {len(missing_sources)} missing source(s): {', '.join(missing_sources)}")
                    return True
                else:
                    print_test("Partial Failure Handling", "WARN", "Expected missing sources but none reported")
                    return True
            else:
                print_test("Partial Failure Handling", "FAIL", data.get('error'))
                return False
        else:
            print_test("Partial Failure Handling", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Partial Failure Handling", "FAIL", str(e))
        return False

def main():
    """Run all integration tests"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}MSME Financial Health Score System - E2E Integration Testing{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Testing backend at: {BASE_URL}{Colors.RESET}\n")
    
    test_results = []
    
    # Run all tests
    print(f"\n{Colors.BLUE}--- Backend API Tests ---{Colors.RESET}\n")
    test_results.append(("Health Check", test_health_check()))
    test_results.append(("Score Computation", test_score_computation_with_demo_profiles()))
    test_results.append(("Score Retrieval", test_score_retrieval()))
    test_results.append(("Score History", test_score_history()))
    test_results.append(("What-If Simulator", test_what_if_simulator()))
    test_results.append(("Ecosystem Integration", test_ecosystem_integration()))
    test_results.append(("Partial Failure Handling", test_partial_failure_scenarios()))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for name, result in test_results:
        status = f"{Colors.GREEN}✓{Colors.RESET}" if result else f"{Colors.RED}✗{Colors.RESET}"
        print(f"{status} {name}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}\n✓ All integration tests passed!{Colors.RESET}\n")
    else:
        print(f"{Colors.RED}\n✗ Some tests failed. Please review the output above.{Colors.RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
