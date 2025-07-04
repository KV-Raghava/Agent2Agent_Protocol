#!/usr/bin/env python3
"""
Test script for the Host Agent API
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8003"  # When using port-forward
# For direct cluster access: API_BASE_URL = "http://host-agent-service:8083"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint test failed: {e}")
        return False

def test_chat(message: str, session_id: str = None, user_id: str = None):
    """Test the chat endpoint"""
    print(f"\n💬 Testing chat with message: '{message}'")
    try:
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        if user_id:
            payload["user_id"] = user_id
            
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            if result.get('tool_calls'):
                print(f"Tool Calls: {json.dumps(result['tool_calls'], indent=2)}")
            if result.get('tool_responses'):
                print(f"Tool Responses: {json.dumps(result['tool_responses'], indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

def test_weather_query():
    """Test weather-related query"""
    return test_chat("What's the weather like in New York today?")

def test_airbnb_query():
    """Test Airbnb-related query"""
    return test_chat("Find me an Airbnb in San Francisco for next weekend")

def test_complex_query():
    """Test a complex query that might use both agents"""
    return test_chat("I'm planning a trip to Tokyo. Can you check the weather there and find me some accommodation options?")

def main():
    """Run all tests"""
    print("🚀 Starting Host Agent API Tests")
    print("=" * 50)
    
    # Test basic endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok:
        print("❌ Health check failed. Make sure the service is running and accessible.")
        return
    
    print("\n" + "=" * 50)
    print("🧪 Testing Chat Functionality")
    
    # Test different types of queries
    tests = [
        ("Simple greeting", lambda: test_chat("Hello, how are you?")),
        ("Weather query", test_weather_query),
        ("Airbnb query", test_airbnb_query),
        ("Complex query", test_complex_query),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📝 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
