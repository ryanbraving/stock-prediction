#!/usr/bin/env python3
"""
Test script for async ML model training workflow
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def test_async_training():
    print("🚀 Testing Async ML Model Training Workflow")
    print("=" * 50)
    
    # Step 1: Start training
    print("1. Starting model training for AAPL...")
    train_response = requests.post(f"{BASE_URL}/train/", 
                                 json={"ticker": "AAPL"})
    
    if train_response.status_code != 200:
        print(f"❌ Training failed: {train_response.text}")
        return
    
    train_data = train_response.json()
    task_id = train_data['task_id']
    print(f"✅ Training started! Task ID: {task_id}")
    print(f"   Message: {train_data['message']}")
    
    # Step 2: Check status periodically
    print("\n2. Monitoring training progress...")
    max_attempts = 30  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        status_response = requests.get(f"{BASE_URL}/task-status/{task_id}/")
        
        if status_response.status_code != 200:
            print(f"❌ Status check failed: {status_response.text}")
            return
        
        status_data = status_response.json()
        status = status_data['status']
        
        print(f"   [{attempt+1:2d}/30] Status: {status}")
        
        if status == 'completed':
            print("✅ Training completed successfully!")
            print(f"   Result: {json.dumps(status_data['result'], indent=2)}")
            break
        elif status == 'failed':
            print(f"❌ Training failed: {status_data['error']}")
            return
        elif status == 'in_progress':
            print(f"   Progress: {status_data.get('progress', 'N/A')}")
        
        time.sleep(10)  # Wait 10 seconds
        attempt += 1
    
    if attempt >= max_attempts:
        print("⏰ Training taking too long, stopping monitoring")
    
    # Step 3: Test prediction with new model
    print("\n3. Testing prediction with trained model...")
    predict_response = requests.post(f"{BASE_URL}/predict/", 
                                   json={"ticker": "AAPL"})
    
    if predict_response.status_code == 200:
        print("✅ Prediction successful!")
        predict_data = predict_response.json()
        print(f"   Model info: {predict_data.get('model_info', 'N/A')}")
    else:
        print(f"❌ Prediction failed: {predict_response.text}")

if __name__ == "__main__":
    test_async_training()