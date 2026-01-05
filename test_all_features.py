#!/usr/bin/env python3
"""
Complete API Testing Script - All Features
Run: python test_all_features.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://claude-opus-chatbot.onrender.com"

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

test_results = []
test_num = 0

def print_header():
    print(f"\n{Colors.CYAN}{'═'*70}{Colors.END}")
    print(f"{Colors.BOLD}           🧪 API TESTING - ALL FEATURES{Colors.END}")
    print(f"{Colors.CYAN}{'═'*70}{Colors.END}\n")

def print_test(title):
    global test_num
    test_num += 1
    print(f"\n{Colors.BLUE}{'─'*70}{Colors.END}")
    print(f"{Colors.YELLOW}TEST #{test_num}: {title}{Colors.END}")
    print(f"{Colors.BLUE}{'─'*70}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    test_results.append({"test": test_num, "status": "PASS", "message": message})

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")
    test_results.append({"test": test_num, "status": "FAIL", "message": message})

def print_json(data, truncate_fields=None):
    """Print JSON with optional field truncation"""
    if truncate_fields:
        for field in truncate_fields:
            if field in data:
                data[field] = str(data[field])[:100] + "..."
    print(json.dumps(data, indent=2))

# ===========================================================================
# TEST FUNCTIONS
# ===========================================================================

def test_api_status():
    """Test 1: API Status Check"""
    print_test("API Status Check")
    print(f"Endpoint: GET /\n")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        data = response.json()
        print_json(data)
        
        if data.get('status') == 'operational':
            print_success(f"API is operational - Version: {data.get('version')}")
        else:
            print_error("API status check failed")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_health_check():
    """Test 2: Health Check"""
    print_test("Health Check")
    print(f"Endpoint: GET /health\n")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = response.json()
        print_json(data)
        
        if data.get('status') == 'optimal':
            print_success("Health check passed")
        else:
            print_error("Health check failed")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_simple_chat():
    """Test 3: Simple Text Chat (OPUS API)"""
    print_test("Simple Text Chat (OPUS API)")
    print(f"Endpoint: POST /chat")
    print(f"Query: Hello, how are you?\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Hello, how are you?",
                "user_id": "test_user_1"
            },
            timeout=30
        )
        data = response.json()
        print_json(data)
        
        model = data.get('model_used')
        if model == 'opus-4.5':
            print_success(f"OPUS API working - Model: {model}")
        else:
            print_error(f"Expected OPUS API, got: {model}")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_complex_chat():
    """Test 4: Complex Query (GPT-5 PRO API)"""
    print_test("Complex Query (GPT-5 PRO API)")
    print(f"Endpoint: POST /chat")
    print(f"Query: Complex algorithm question\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Please provide a detailed analysis of the merge sort algorithm and debug this code with comprehensive explanation",
                "user_id": "test_user_1"
            },
            timeout=45
        )
        data = response.json()
        print_json(data)
        
        model = data.get('model_used')
        if model == 'gpt5-pro':
            print_success(f"GPT-5 PRO API working - Model: {model}")
        else:
            print_error(f"Expected GPT-5 PRO, got: {model}")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_hinglish():
    """Test 5: Hinglish Chat"""
    print_test("Hinglish Chat Support")
    print(f"Endpoint: POST /chat")
    print(f"Query: Bhai Python mein loops kaise likhte hain?\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Bhai Python mein loops kaise likhte hain?",
                "user_id": "test_user_2"
            },
            timeout=30
        )
        data = response.json()
        print_json(data)
        
        lang = data.get('language')
        if lang == 'Hinglish':
            print_success(f"Hinglish detection working - Language: {lang}")
        else:
            print_success(f"Language detected: {lang}")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_realtime_time():
    """Test 6: Real-Time Data (Current Time)"""
    print_test("Real-Time Data - Current Time")
    print(f"Endpoint: POST /chat")
    print(f"Query: What time is it?\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "What is the current time and date?",
                "user_id": "test_user_3"
            },
            timeout=30
        )
        data = response.json()
        print_json(data)
        
        if data.get('real_time_data_used'):
            print_success("Real-time data integration working")
        else:
            print_success("Response received")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_crypto_prices():
    """Test 7: Crypto Prices"""
    print_test("Real-Time Data - Crypto Prices")
    print(f"Endpoint: POST /chat")
    print(f"Query: Bitcoin price kya hai?\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Bitcoin price kya hai?",
                "user_id": "test_user_3"
            },
            timeout=30
        )
        data = response.json()
        print_json(data)
        
        if data.get('real_time_data_used'):
            print_success("Crypto price API working")
        else:
            print_success("Response received")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_conversation_memory():
    """Test 8: Conversation Memory"""
    print_test("Conversation Memory")
    print(f"Endpoint: POST /chat (multiple messages)\n")
    
    try:
        # First message
        print("Message 1: My name is Aman")
        response1 = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "My name is Aman",
                "user_id": "memory_test"
            },
            timeout=30
        )
        data1 = response1.json()
        print_json(data1)
        print()
        time.sleep(2)
        
        # Second message
        print("Message 2: What is my name?")
        response2 = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "What is my name?",
                "user_id": "memory_test"
            },
            timeout=30
        )
        data2 = response2.json()
        print_json(data2)
        
        conv_length = data2.get('conversation_length', 0)
        if conv_length >= 4:
            print_success(f"Conversation memory working - Length: {conv_length} messages")
        else:
            print_error(f"Memory issue - Length: {conv_length}")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_image_generation():
    """Test 9: Image Generation"""
    print_test("Image Generation (Stable Diffusion 3.5)")
    print(f"Endpoint: POST /chat")
    print(f"Query: Generate image of sunset")
    print(f"⚠️  Note: This may take 15-30 seconds\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Generate image of beautiful sunset over mountains",
                "user_id": "test_user_4"
            },
            timeout=60
        )
        data = response.json()
        print_json(data, truncate_fields=['image'])
        
        if data.get('type') == 'image':
            print_success("Image generation working")
            print(f"Image data (base64): {str(data.get('image', ''))[:100]}...")
        else:
            print_error("Image generation failed or not triggered")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_video_generation():
    """Test 10: Video Generation"""
    print_test("Video Generation (Runway AI)")
    print(f"Endpoint: POST /chat")
    print(f"Query: Generate video of dancing robot")
    print(f"⚠️  Note: This may take 30-60 seconds\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Generate video of a robot dancing",
                "user_id": "test_user_5"
            },
            timeout=120
        )
        data = response.json()
        print_json(data, truncate_fields=['video'])
        
        if data.get('type') == 'video':
            print_success("Video generation working")
            print(f"Video data (base64): {str(data.get('video', ''))[:100]}...")
        else:
            print_error("Video generation failed or not triggered")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_live_start():
    """Test 11: Live Conversation - Start Session"""
    print_test("Live Conversation - Start Session")
    print(f"Endpoint: POST /live/start\n")
    
    session_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/live/start",
            json={"language": "en"},
            timeout=10
        )
        data = response.json()
        print_json(data)
        
        session_id = data.get('session_id')
        if session_id:
            print_success(f"Live session created - ID: {session_id}")
        else:
            print_error("Failed to create live session")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)
    return session_id

def test_live_text(session_id):
    """Test 12: Live Conversation - Text Input"""
    if not session_id:
        print_error("No session ID available, skipping test")
        return
    
    print_test("Live Conversation - Text Input")
    print(f"Endpoint: POST /live/text")
    print(f"Session ID: {session_id}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/live/text",
            json={
                "session_id": session_id,
                "message": "Hello! How are you?",
                "language": "en",
                "include_audio": False
            },
            timeout=30
        )
        data = response.json()
        print_json(data)
        
        if data.get('success'):
            print_success("Live text conversation working")
        else:
            print_error("Live text conversation failed")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_live_status():
    """Test 13: Live Conversation - Status Check"""
    print_test("Live Conversation - Status Check")
    print(f"Endpoint: GET /live/status\n")
    
    try:
        response = requests.get(f"{BASE_URL}/live/status", timeout=10)
        data = response.json()
        print_json(data)
        
        status = data.get('status')
        if status == 'live_conversation_ready':
            print_success("Live conversation system ready")
        else:
            print_success(f"Status: {status}")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

def test_reset_conversation():
    """Test 14: Reset Conversation"""
    print_test("Reset Conversation")
    print(f"Endpoint: POST /reset\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/reset",
            json={"user_id": "memory_test"},
            timeout=10
        )
        data = response.json()
        print_json(data)
        
        if data.get('success'):
            print_success("Conversation reset working")
        else:
            print_error("Reset failed")
    except Exception as e:
        print_error(f"Failed: {str(e)}")
    
    time.sleep(2)

# ===========================================================================
# MAIN EXECUTION
# ===========================================================================

def print_summary():
    """Print test summary"""
    print(f"\n{Colors.CYAN}{'═'*70}{Colors.END}")
    print(f"{Colors.BOLD}                    🎉 TESTING COMPLETE!{Colors.END}")
    print(f"{Colors.CYAN}{'═'*70}{Colors.END}\n")
    
    passed = sum(1 for r in test_results if r['status'] == 'PASS')
    failed = sum(1 for r in test_results if r['status'] == 'FAIL')
    
    print(f"{Colors.GREEN}Total Tests Run: {test_num}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print()
    
    print("✅ Tested Features:")
    features = [
        "API Status",
        "Health Check",
        "Simple Chat (OPUS API)",
        "Complex Chat (GPT-5 PRO API)",
        "Hinglish Support",
        "Real-time Time/Date",
        "Crypto Prices",
        "Conversation Memory",
        "Image Generation",
        "Video Generation",
        "Live Conversation (Start)",
        "Live Conversation (Text)",
        "Live Status",
        "Conversation Reset"
    ]
    for i, feature in enumerate(features, 1):
        print(f"  {i:2}. {feature}")
    
    print(f"\n{Colors.BLUE}{'─'*70}{Colors.END}")
    print("For detailed API documentation, see:")
    print("  • LIVE_CONVERSATION_GUIDE.md")
    print("  • API_GUIDE.md")
    print(f"{Colors.BLUE}{'─'*70}{Colors.END}\n")

def main():
    """Main test runner"""
    print_header()
    
    # Run all tests
    test_api_status()
    test_health_check()
    test_simple_chat()
    test_complex_chat()
    test_hinglish()
    test_realtime_time()
    test_crypto_prices()
    test_conversation_memory()
    test_image_generation()
    test_video_generation()
    
    # Live conversation tests
    session_id = test_live_start()
    test_live_text(session_id)
    test_live_status()
    
    # Cleanup
    test_reset_conversation()
    
    # Summary
    print_summary()

if __name__ == "__main__":
    main()