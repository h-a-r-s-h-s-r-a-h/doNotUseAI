import requests
import json

BASE_URL = "http://localhost:5001"

def test_chat():
    """Test the chat endpoint"""
    print("\n=== Testing Chat Endpoint ===")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "Hello, how are you?"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_audio_upload():
    """Test the audio upload endpoint"""
    print("\n=== Testing Audio Upload Endpoint ===")
    files = {
        'file': ('test_audio.wav', open('test_audio.wav', 'rb')),
    }
    data = {
        'message': 'Please analyze this audio',
        'type': 'audio'
    }
    response = requests.post(
        f"{BASE_URL}/api/upload",
        files=files,
        data=data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_image_upload():
    """Test the image upload endpoint"""
    print("\n=== Testing Image Upload Endpoint ===")
    files = {
        'file': ('test_image.png', open('test_image.png', 'rb')),
    }
    data = {
        'message': 'Please analyze this image',
        'type': 'image'
    }
    response = requests.post(
        f"{BASE_URL}/api/upload",
        files=files,
        data=data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_webpage():
    """Test the webpage endpoint"""
    print("\n=== Testing Webpage Endpoint ===")
    response = requests.post(
        f"{BASE_URL}/api/webpage",
        json={
            "url": "https://example.com",
            "message": "Please analyze this webpage"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    # Test all endpoints
    test_chat()
    test_audio_upload()
    test_image_upload()
    test_webpage() 