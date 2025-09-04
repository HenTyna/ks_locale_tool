#!/usr/bin/env python3
"""
Simple test script for the Locale Tool API
Run this after installing Flask dependencies to test the API functionality
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    print("Testing Locale Tool API...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/api/health/")
        print(f"Health check: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Please start it with: python app.py")
        print("📖 Swagger UI will be available at: http://localhost:5000/docs/")
        return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test search endpoint
    test_content = '''
    <div>
        <span>안녕하세요</span>
        <button>클릭하세요</button>
        <input placeholder="검색어를 입력하세요" />
        <p>Hello World</p>
    </div>
    '''
    
    try:
        response = requests.post(f"{base_url}/api/search/", 
                               json={"content": test_content})
        result = response.json()
        print(f"Search test: {response.status_code}")
        print(f"Found {result.get('count', 0)} untemplated elements")
        if result.get('elements'):
            for i, element in enumerate(result['elements'][:3]):  # Show first 3
                print(f"  {i+1}. {element.get('korean_texts', [])}")
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    # Test apply endpoint
    try:
        response = requests.post(f"{base_url}/api/apply/", 
                               json={"content": test_content, "template_type": "bt"})
        result = response.json()
        print(f"Apply test: {response.status_code}")
        if result.get('success'):
            print(f"Applied {result.get('replacements_count', 0)} templates")
            print("Sample result:")
            print(result.get('updated_content', '')[:200] + "...")
        else:
            print(f"Apply failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Apply test failed: {e}")
    
    print("\n✅ API tests completed!")

if __name__ == "__main__":
    test_api()
