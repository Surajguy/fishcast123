#!/usr/bin/env python3
"""
Simple test script for the FishCast API
"""
import requests
import os

def test_analyze_endpoint():
    """Test the /api/analyze endpoint with a sample image"""
    
    # API endpoint
    url = "http://localhost:8000/api/analyze"
    
    # You can test with any image file
    # For testing, you might want to use a sample fishing spot image
    image_path = input("Enter path to a fishing spot image (or press Enter to skip): ").strip()
    
    if not image_path or not os.path.exists(image_path):
        print("No valid image path provided. Skipping test.")
        return
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {'file': ('fishing_spot.jpg', image_file, 'image/jpeg')}
            
            print("Sending image to FishCast API...")
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success!")
                print(f"Recommendation: {result.get('recommendation', 'No recommendation')}")
                print(f"API Provider: {result.get('api_provider', 'Unknown')}")
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ Health Check:")
            print(f"  Status: {result.get('status')}")
            print(f"  Service: {result.get('service')}")
            print(f"  AI Provider: {result.get('ai_provider')}")
            print(f"  API Configured: {result.get('api_configured')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")

if __name__ == "__main__":
    print("🎣 FishCast API Test Script")
    print("=" * 40)
    
    # Test health endpoint first
    test_health_endpoint()
    print()
    
    # Test analyze endpoint
    test_analyze_endpoint()
