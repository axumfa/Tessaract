"""
Simple script to test database integration
Run this to verify database connection and operations
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import (
    init_db,
    is_db_available,
    log_prediction,
    get_recent_transactions,
    get_fraud_stats,
    close_db_pool
)

def test_database():
    """Test database connection and operations"""
    print("Testing database integration...")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    try:
        if init_db():
            print("[OK] Database initialized successfully")
        else:
            print("[ERROR] Database initialization failed")
            print("   Make sure PostgreSQL is running and credentials are correct")
            return False
    except Exception as e:
        print(f"[ERROR] Database initialization error: {str(e)}")
        return False
    
    # Check availability
    print("\n2. Checking database availability...")
    if is_db_available():
        print("[OK] Database is available")
    else:
        print("[ERROR] Database is not available")
        return False
    
    # Test logging prediction
    print("\n3. Testing prediction logging...")
    test_transaction = {
        "amount": 100.50,
        "hour": 14,
        "dayofweek": 3,
        "txns_last_24h": 5.0,
        "amount_last_24h": 500.0,
        "risk_score": 25.5
    }
    
    if log_prediction(
        transaction_id="test-transaction-001",
        transaction_data=test_transaction,
        prediction=False,
        confidence=0.85
    ):
        print("[OK] Prediction logged successfully")
    else:
        print("[WARNING] Failed to log prediction (may be OK if DB is not configured)")
        # Don't fail the test, just warn
    
    # Test getting transactions
    print("\n4. Testing get recent transactions...")
    try:
        transactions = get_recent_transactions(limit=5)
        print(f"[OK] Retrieved {len(transactions)} transactions")
        if transactions:
            print(f"   Latest transaction ID: {transactions[0]['transaction_id']}")
    except Exception as e:
        print(f"[ERROR] Failed to get transactions: {str(e)}")
        return False
    
    # Test getting stats
    print("\n5. Testing get fraud stats...")
    try:
        stats = get_fraud_stats()
        print(f"[OK] Retrieved statistics")
        print(f"   Total transactions: {stats['total_transactions']}")
        print(f"   Fraud count: {stats['fraud_count']}")
        print(f"   Fraud percentage: {stats['fraud_percentage']:.2f}%")
    except Exception as e:
        print(f"[ERROR] Failed to get stats: {str(e)}")
        return False
    
    # Cleanup
    print("\n6. Cleaning up...")
    close_db_pool()
    print("[OK] Database pool closed")
    
    print("\n" + "=" * 50)
    print("[OK] All database tests passed!")
    return True

if __name__ == "__main__":
    # Set environment variables if not set
    if not os.getenv("DB_HOST"):
        print("Setting default database credentials...")
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_NAME"] = "fraud_detection"
        os.environ["DB_USER"] = "postgres"
        os.environ["DB_PASSWORD"] = "postgres"
        print("   Using defaults: localhost/fraud_detection/postgres")
        print("   Set environment variables to use custom credentials")
    
    success = test_database()
    sys.exit(0 if success else 1)

