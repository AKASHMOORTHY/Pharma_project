#!/usr/bin/env python3
"""
Test script to verify Celery configuration is working properly
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_celery_imports():
    """Test that all Celery-related modules can be imported without errors"""
    try:
        from app.tasks.locking import celery
        print("✅ Celery app imported successfully from locking.py")
        
        from app.tasks.anomaly_checks import run_hourly_anomaly_check
        print("✅ Hourly runner task imported successfully")
        
        from app.ml.predict_from_db import predict_anomalies_from_db
        print("✅ ML predictor task imported successfully")
        
        from app.tasks.notification import send_email_alert
        print("✅ Notification task imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error importing Celery modules: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_celery_configuration():
    """Test that Celery configuration is properly set up"""
    try:
        from app.tasks.locking import celery
        
        # Check basic configuration
        print(f"✅ Celery app name: {celery.main}")
        print(f"✅ Broker URL: {celery.conf.broker_url}")
        print(f"✅ Result backend: {celery.conf.result_backend}")
        print(f"✅ Worker pool: {celery.conf.worker_pool}")
        print(f"✅ Prefetch multiplier: {celery.conf.worker_prefetch_multiplier}")
        
        # Check beat schedule
        beat_schedule = celery.conf.beat_schedule
        print(f"✅ Beat schedule has {len(beat_schedule)} tasks:")
        for task_name, task_config in beat_schedule.items():
            print(f"   - {task_name}: {task_config['task']}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking Celery configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Celery tests"""
    print("🔍 Testing Celery Configuration")
    print("=" * 40)
    
    tests = [
        ("Celery Imports", test_celery_imports),
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
        print("🎉 All Celery tests passed! Your Celery configuration is working properly.")
        print("\n📝 To run Celery worker:")
        print("   celery -A app.celery_worker.celery worker --loglevel=info")
        print("   celery -A app.celery_worker.celery worker --pool=solo --loglevel=info")
        print("\n📝 To run Celery beat:")
        print("   celery -A app.celery_worker.celery beat --loglevel=info")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 