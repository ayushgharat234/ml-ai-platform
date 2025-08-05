#!/usr/bin/env python3
"""
Test script for the AI Platform API
"""
import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing AI Platform API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
        else:
            print(f"Health check failed: {response.text}")
    except Exception as e:
        print(f"Health check error: {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Root response: {response.json()}")
    except Exception as e:
        print(f"Root endpoint error: {e}")
    
    # Test prediction endpoint
    test_features = [5.1, 3.5, 1.4, 0.2]  # Iris dataset features
    try:
        response = requests.post(
            f"{base_url}/predict/",
            json={"features": test_features}
        )
        print(f"Prediction endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Prediction: {result['prediction']}")
            print(f"Probabilities: {result['probabilities']}")
        else:
            print(f"Prediction failed: {response.text}")
    except Exception as e:
        print(f"Prediction error: {e}")

if __name__ == "__main__":
    test_api() 