#!/usr/bin/env python3
"""
Script to restart Celery with proper configuration
"""

import os
import sys
import subprocess
import time

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        response = r.ping()
        print(f"✅ Redis is running: {response}")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("Please start Redis server first:")
        print("   redis-server")
        return False

def stop_celery_processes():
    """Stop any running Celery processes"""
    try:
        # On Windows, we need to find and kill Celery processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'celery' in result.stdout.lower():
            print("🛑 Stopping existing Celery processes...")
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True)
            time.sleep(2)
            print("✅ Celery processes stopped")
        else:
            print("✅ No existing Celery processes found")
            
    except Exception as e:
        print(f"⚠️ Could not stop Celery processes: {e}")

def start_celery_worker():
    """Start Celery worker"""
    print("🚀 Starting Celery worker...")
    try:
        # Start worker in background
        worker_cmd = [
            sys.executable, '-m', 'celery', '-A', 'app.celery_worker.celery_app',
            'worker', '--pool=solo', '--loglevel=info'
        ]
        
        worker_process = subprocess.Popen(
            worker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Celery worker started with PID: {worker_process.pid}")
        return worker_process
        
    except Exception as e:
        print(f"❌ Failed to start Celery worker: {e}")
        return None

def start_celery_beat():
    """Start Celery beat scheduler"""
    print("⏰ Starting Celery beat scheduler...")
    try:
        # Start beat in background
        beat_cmd = [
            sys.executable, '-m', 'celery', '-A', 'app.celery_worker.celery_app',
            'beat', '--loglevel=info'
        ]
        
        beat_process = subprocess.Popen(
            beat_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Celery beat started with PID: {beat_process.pid}")
        return beat_process
        
    except Exception as e:
        print(f"❌ Failed to start Celery beat: {e}")
        return None

def main():
    """Main function to restart Celery"""
    print("🔄 Restarting Celery with Database Session Fixes")
    print("=" * 50)
    
    # Check Redis first
    if not check_redis():
        return False
    
    # Stop existing processes
    stop_celery_processes()
    
    # Start worker
    worker_process = start_celery_worker()
    if not worker_process:
        return False
    
    # Wait a moment for worker to start
    time.sleep(3)
    
    # Start beat
    beat_process = start_celery_beat()
    if not beat_process:
        worker_process.terminate()
        return False
    
    print("\n🎉 Celery restarted successfully!")
    print("📝 Worker and Beat are running in the background")
    print("📝 Check the logs for any errors")
    print("\n📝 To stop Celery:")
    print("   Press Ctrl+C or run: taskkill /F /IM python.exe")
    
    try:
        # Keep the script running to monitor processes
        while True:
            time.sleep(10)
            if worker_process.poll() is not None:
                print("⚠️ Celery worker stopped unexpectedly")
                break
            if beat_process.poll() is not None:
                print("⚠️ Celery beat stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping Celery processes...")
        worker_process.terminate()
        beat_process.terminate()
        print("✅ Celery processes stopped")

if __name__ == "__main__":
    main()
