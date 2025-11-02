"""
Comprehensive test suite for Fraud Detection API
Tests all endpoints, database integration, and functionality
"""
import os
import sys
import time
import json
import requests
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_RESULTS = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tests": []
}


def log_test(name: str, passed: bool, message: str = "", warning: bool = False):
    """Log test result"""
    status = "PASS" if passed else "WARN" if warning else "FAIL"
    symbol = "[OK]" if passed else "[WARN]" if warning else "[FAIL]"
    
    TEST_RESULTS["tests"].append({
        "name": name,
        "status": status,
        "message": message
    })
    
    if passed:
        TEST_RESULTS["passed"] += 1
        print(f"{symbol} {name}")
    elif warning:
        TEST_RESULTS["warnings"] += 1
        print(f"{symbol} {name} - {message}")
    else:
        TEST_RESULTS["failed"] += 1
        print(f"{symbol} {name} - {message}")


def test_api_health():
    """Test 1: API Health Check"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            model_loaded = data.get("model_loaded", False)
            db_connected = data.get("database_connected", False)
            
            log_test("API Health Check", True, f"Status: {data.get('status')}")
            log_test("Model Loaded", model_loaded, 
                    "Model not loaded - predictions won't work" if not model_loaded else "")
            log_test("Database Connected", db_connected,
                    "Database not connected - data won't be saved" if not db_connected else "")
            return True
        else:
            log_test("API Health Check", False, f"HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_test("API Health Check", False, "Cannot connect to API. Is it running?")
        return False
    except Exception as e:
        log_test("API Health Check", False, str(e))
        return False


def test_home_endpoint():
    """Test 2: Home Endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            log_test("Home Endpoint", True)
            return True
        else:
            log_test("Home Endpoint", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Home Endpoint", False, str(e))
        return False


def test_single_prediction():
    """Test 3: Single Prediction"""
    try:
        transaction = {
            "amount": 100.50,
            "hour": 14,
            "dayofweek": 3,
            "txns_last_24h": 5.0,
            "amount_last_24h": 500.0,
            "risk_score": 25.5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=transaction,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["transaction_id", "is_fraud", "confidence", "timestamp"]
            missing = [f for f in required_fields if f not in data]
            
            if not missing:
                log_test("Single Prediction", True, 
                        f"Transaction ID: {data['transaction_id'][:8]}..., "
                        f"Fraud: {data['is_fraud']}, "
                        f"Confidence: {data['confidence']:.2%}")
                return data["transaction_id"]
            else:
                log_test("Single Prediction", False, f"Missing fields: {missing}")
                return None
        else:
            log_test("Single Prediction", False, f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Single Prediction", False, str(e))
        return None


def test_batch_prediction():
    """Test 4: Batch Prediction"""
    try:
        transactions = {
            "transactions": [
                {
                    "amount": 50.00,
                    "hour": 10,
                    "dayofweek": 1,
                    "txns_last_24h": 3.0,
                    "amount_last_24h": 150.0,
                    "risk_score": 15.0
                },
                {
                    "amount": 5000.00,
                    "hour": 2,
                    "dayofweek": 0,
                    "txns_last_24h": 1.0,
                    "amount_last_24h": 5000.0,
                    "risk_score": 10000.0
                }
            ]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict/batch",
            json=transactions,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "predictions" in data and "summary" in data:
                summary = data["summary"]
                log_test("Batch Prediction", True,
                        f"Processed: {summary.get('total_transactions', 0)}, "
                        f"Fraud: {summary.get('fraud_count', 0)}")
                return True
            else:
                log_test("Batch Prediction", False, "Missing predictions or summary")
                return False
        else:
            log_test("Batch Prediction", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Batch Prediction", False, str(e))
        return False


def test_get_transactions(transaction_id: str = None):
    """Test 5: Get Recent Transactions"""
    try:
        response = requests.get(f"{API_BASE_URL}/transactions?limit=10", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "transactions" in data:
                count = len(data["transactions"])
                log_test("Get Transactions", True, f"Retrieved {count} transactions")
                
                # Check if our test transaction is there
                if transaction_id:
                    found = any(t.get("transaction_id") == transaction_id 
                               for t in data["transactions"])
                    if found:
                        log_test("Transaction Saved to DB", True, 
                                "Test transaction found in database")
                    else:
                        log_test("Transaction Saved to DB", False,
                                "Test transaction not found (may need to wait or DB not connected)")
                
                return True
            else:
                log_test("Get Transactions", False, "Missing transactions field")
                return False
        elif response.status_code == 503:
            log_test("Get Transactions", False, 
                    "Database not available (503)", warning=True)
            return False
        else:
            log_test("Get Transactions", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Get Transactions", False, str(e))
        return False


def test_get_stats():
    """Test 6: Get Statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["total_transactions", "fraud_count", "fraud_percentage"]
            missing = [f for f in required_fields if f not in data]
            
            if not missing:
                total = data["total_transactions"]
                fraud = data["fraud_count"]
                percentage = data["fraud_percentage"]
                log_test("Get Statistics", True,
                        f"Total: {total}, Fraud: {fraud} ({percentage:.2f}%)")
                return True
            else:
                log_test("Get Statistics", False, f"Missing fields: {missing}")
                return False
        elif response.status_code == 503:
            log_test("Get Statistics", False,
                    "Database not available (503)", warning=True)
            return False
        else:
            log_test("Get Statistics", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Get Statistics", False, str(e))
        return False


def test_multiple_predictions():
    """Test 7: Multiple Predictions (stress test)"""
    try:
        transactions = []
        for i in range(5):
            transactions.append({
                "amount": 100.0 + (i * 10),
                "hour": i % 24,
                "dayofweek": i % 7,
                "txns_last_24h": 5.0 + i,
                "amount_last_24h": 500.0 + (i * 100),
                "risk_score": 25.0 + (i * 5)
            })
        
        batch = {"transactions": transactions}
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/predict/batch",
            json=batch,
            timeout=20
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            log_test("Multiple Predictions (5)", True,
                    f"Processed in {elapsed:.2f}s")
            return True
        else:
            log_test("Multiple Predictions (5)", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Multiple Predictions (5)", False, str(e))
        return False


def test_invalid_input():
    """Test 8: Invalid Input Handling"""
    try:
        # Missing required fields
        invalid_transaction = {
            "amount": 100.0
            # Missing other required fields
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid_transaction,
            timeout=5
        )
        
        # Should return 422 (validation error) or 400 (bad request)
        if response.status_code in [400, 422]:
            log_test("Invalid Input Handling", True,
                    f"Correctly rejected with HTTP {response.status_code}")
            return True
        else:
            log_test("Invalid Input Handling", False,
                    f"Expected 400/422, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Invalid Input Handling", False, str(e))
        return False


def test_edge_cases():
    """Test 9: Edge Cases"""
    try:
        # Very large amount
        large_transaction = {
            "amount": 999999.99,
            "hour": 23,
            "dayofweek": 6,
            "txns_last_24h": 100.0,
            "amount_last_24h": 1000000.0,
            "risk_score": 999999.0
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=large_transaction,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("Edge Cases (Large Amounts)", True)
            return True
        else:
            log_test("Edge Cases (Large Amounts)", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Edge Cases (Large Amounts)", False, str(e))
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Fraud Detection API - Comprehensive Test Suite")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print("")
    
    # Run tests
    print("Running tests...")
    print("-" * 60)
    
    # Basic connectivity
    api_available = test_api_health()
    if not api_available:
        print("\n[ERROR] API is not available. Please start the API first:")
        print("  .\\run.bat")
        return
    
    test_home_endpoint()
    
    # Core functionality
    transaction_id = test_single_prediction()
    test_batch_prediction()
    test_multiple_predictions()
    
    # Database integration
    time.sleep(1)  # Wait a bit for DB to save
    test_get_transactions(transaction_id)
    test_get_stats()
    
    # Error handling
    test_invalid_input()
    test_edge_cases()
    
    # Summary
    print("-" * 60)
    print("\nTest Summary:")
    print(f"  Passed:  {TEST_RESULTS['passed']}")
    print(f"  Failed:  {TEST_RESULTS['failed']}")
    print(f"  Warnings: {TEST_RESULTS['warnings']}")
    print(f"  Total:   {len(TEST_RESULTS['tests'])}")
    
    # Detailed results
    print("\nDetailed Results:")
    for test in TEST_RESULTS['tests']:
        status = test['status']
        name = test['name']
        message = test['message']
        if message:
            print(f"  {status:4} - {name:40} - {message}")
        else:
            print(f"  {status:4} - {name:40}")
    
    print("\n" + "=" * 60)
    
    if TEST_RESULTS['failed'] == 0:
        print("[SUCCESS] All critical tests passed!")
        if TEST_RESULTS['warnings'] > 0:
            print(f"[WARNING] {TEST_RESULTS['warnings']} warnings (non-critical)")
        return 0
    else:
        print(f"[FAILURE] {TEST_RESULTS['failed']} test(s) failed")
        return 1


if __name__ == "__main__":
    # Check if API URL is different
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    
    exit_code = main()
    sys.exit(exit_code)

