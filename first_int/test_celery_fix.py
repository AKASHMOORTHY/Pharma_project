#!/usr/bin/env python3
"""
Test script to verify the Celery database session fixes
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_database_sessions():
    """Test that database sessions are properly managed"""
    try:
        from app.tasks.anomaly_checks import check_missed_entries, check_logical_sequence
        from app.ml.predict_from_db import predict_anomalies_from_db
        
        print("🧪 Testing database session management...")
        
        # Test anomaly checks
        print("Testing check_missed_entries...")
        check_missed_entries()
        
        print("Testing check_logical_sequence...")
        check_logical_sequence()
        
        print("Testing ML prediction...")
        predict_anomalies_from_db()
        
        print("✅ All database session tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database session test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_celery_configuration():
    """Test that Celery configuration is consistent"""
    try:
        from app.tasks.celery_utils import celery_app
        from app.tasks.locking import celery as locking_celery
        
        print("🧪 Testing Celery configuration consistency...")
        
        # Check that both Celery instances use the same Redis port
        main_broker = celery_app.conf.broker_url
        locking_broker = locking_celery.conf.broker_url
        
        print(f"Main Celery broker: {main_broker}")
        print(f"Locking Celery broker: {locking_broker}")
        
        if "6379" in main_broker and "6379" in locking_broker:
            print("✅ Both Celery instances use consistent Redis port (6379)")
        else:
            print("⚠️ Celery instances use different Redis ports")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Celery Database Session Fixes")
    print("=" * 50)
    
    tests = [
        ("Database Sessions", test_database_sessions),
        ("Celery Configuration", test_celery_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed!")
        else:
            print(f"❌ {test_name} test failed!")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Celery database session issues should be resolved.")
        print("\n📝 To run Celery worker:")
        print("   celery -A app.celery_worker.celery_app worker --loglevel=info")
        print("   celery -A app.celery_worker.celery_app worker --pool=solo --loglevel=info")
        print("\n📝 To run Celery beat:")
        print("   celery -A app.celery_worker.celery_app beat --loglevel=info")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
