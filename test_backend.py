#!/usr/bin/env python3
"""
Quick test script to diagnose backend issues
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\nTesting chat endpoint...")
    try:
        payload = {
            "message": "Hello, this is a test",
            "conversation_history": []
        }
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Error details: {e.response.json()}")
            except:
                print(f"Error text: {e.response.text}")
        return False

def check_env():
    """Check environment variables"""
    print("\nChecking environment variables...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✓ GEMINI_API_KEY is set (length: {len(api_key)})")
        return True
    else:
        print("✗ GEMINI_API_KEY is not set")
        print("  Please create a .env file with: GEMINI_API_KEY=your_key_here")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Backend Diagnostic Test")
    print("=" * 50)
    
    env_ok = check_env()
    health_ok = test_health()
    chat_ok = test_chat() if health_ok else False
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Environment: {'✓' if env_ok else '✗'}")
    print(f"  Health Check: {'✓' if health_ok else '✗'}")
    print(f"  Chat Endpoint: {'✓' if chat_ok else '✗'}")
    print("=" * 50)

