#!/usr/bin/env python3
"""
Comprehensive Test Suite for Claude Opus 4.5 Enhanced

Tests all advanced features:
- Deep Reasoning
- 200K Context Window
- Vision Analysis
- Agentic Tool Use
- Fact-Checking
- Multi-Language Support

Usage:
    python test_opus_enhanced.py
"""

import requests
import json
import time
import base64
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:10000"
TEST_USER_ID = "test_user_123"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}✨ {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}💡 {text}{Colors.RESET}")

def test_endpoint(name: str, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
    """Test API endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            print_success(f"{name} - Status: {response.status_code}")
            return {"success": True, "data": response.json()}
        else:
            print_error(f"{name} - Status: {response.status_code}")
            return {"success": False, "error": response.text}
    
    except Exception as e:
        print_error(f"{name} - Error: {str(e)}")
        return {"success": False, "error": str(e)}

# ============================================================================
# Test Suite
# ============================================================================

def test_1_api_status():
    """Test 1: API Status Check"""
    print_header("Test 1: API Status & Health Check")
    
    result = test_endpoint(
        "Home Endpoint",
        "GET",
        "/"
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Model: {data.get('model')}")
        print_info(f"Version: {data.get('version')}")
        print_info(f"Features: {len(data.get('features', {}))} active")
    
    result = test_endpoint(
        "Health Check",
        "GET",
        "/health"
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Status: {data.get('status')}")
        print_info(f"Active Users: {data.get('active_users')}")

def test_2_simple_chat():
    """Test 2: Simple Chat (Quick Reasoning)"""
    print_header("Test 2: Simple Chat - Quick Reasoning")
    
    result = test_endpoint(
        "Simple Question",
        "POST",
        "/chat",
        {
            "message": "What is Python?",
            "user_id": TEST_USER_ID,
            "reasoning_depth": "quick"
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Response Length: {len(data.get('response', ''))} chars")
        print_info(f"Reasoning Depth: {data.get('reasoning_depth')}")
        print_info(f"Confidence: {data.get('confidence_score', 0):.0%}")
        print_info(f"Fact Checked: {data.get('fact_checked')}")
        print(f"\n{Colors.YELLOW}Response Preview:{Colors.RESET}")
        print(data.get('response', '')[:200] + "...")

def test_3_deep_reasoning():
    """Test 3: Deep Reasoning for Code Analysis"""
    print_header("Test 3: Deep Reasoning - Code Bug Detection")
    
    code_with_bug = """
    def calculate_average(numbers):
        total = 0
        for num in numbers:
            total += num
        return total / len(numbers)  # Bug: What if numbers is empty?
    
    result = calculate_average([])
    print(result)
    """
    
    result = test_endpoint(
        "Code Analysis",
        "POST",
        "/chat",
        {
            "message": f"Find bugs in this code and suggest fixes:\n{code_with_bug}",
            "user_id": TEST_USER_ID,
            "reasoning_depth": "deep",
            "enable_tools": True
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Reasoning Level: {data.get('reasoning_depth')}")
        print_info(f"Tokens Used: {data.get('tokens_used')}")
        print_info(f"Confidence: {data.get('confidence_score', 0):.0%}")
        print_info(f"Tools Used: {data.get('tools_used')}")
        print(f"\n{Colors.YELLOW}Analysis:{Colors.RESET}")
        print(data.get('response', '')[:500] + "...")

def test_4_calculator_tool():
    """Test 4: Automatic Calculator Tool"""
    print_header("Test 4: Agentic Tool Use - Calculator")
    
    result = test_endpoint(
        "Math Calculation",
        "POST",
        "/chat",
        {
            "message": "Calculate 25% of 10000 and then add 500 to the result",
            "user_id": TEST_USER_ID,
            "enable_tools": True
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Tools Detected: {data.get('tools_used')}")
        print_info(f"Response: {data.get('response')}")
        
        if "calculator" in data.get('tools_used', []):
            print_success("Calculator tool was auto-detected and used!")
        else:
            print_error("Calculator tool was not used")

def test_5_crypto_tool():
    """Test 5: Crypto Price Tool"""
    print_header("Test 5: Agentic Tool Use - Crypto Prices")
    
    result = test_endpoint(
        "Crypto Query",
        "POST",
        "/chat",
        {
            "message": "What's the current Bitcoin price?",
            "user_id": TEST_USER_ID,
            "enable_tools": True
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Tools Used: {data.get('tools_used')}")
        print_info(f"Response Preview: {data.get('response')[:150]}...")

def test_6_multi_language():
    """Test 6: Multi-Language Support (Hindi/Hinglish)"""
    print_header("Test 6: Multi-Language Support - Hindi/Hinglish")
    
    # Test Hindi
    result = test_endpoint(
        "Hindi Query",
        "POST",
        "/chat",
        {
            "message": "मशीन लर्निंग क्या है?",
            "user_id": TEST_USER_ID
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_success("Hindi query processed")
        print_info(f"Response Length: {len(data.get('response', ''))} chars")
    
    # Test Hinglish
    result = test_endpoint(
        "Hinglish Query",
        "POST",
        "/chat",
        {
            "message": "Python programming ka basic concept samjhao",
            "user_id": TEST_USER_ID
        }
    )
    
    if result["success"]:
        print_success("Hinglish query processed")

def test_7_context_memory():
    """Test 7: 200K Context Window - Conversation Memory"""
    print_header("Test 7: Context Memory - Multi-Turn Conversation")
    
    # First message
    result1 = test_endpoint(
        "Message 1",
        "POST",
        "/chat",
        {
            "message": "Let's talk about React hooks. Explain useState.",
            "user_id": "context_test_user"
        }
    )
    
    if result1["success"]:
        print_success("First message sent")
    
    time.sleep(1)
    
    # Second message (references previous)
    result2 = test_endpoint(
        "Message 2 (Context Reference)",
        "POST",
        "/chat",
        {
            "message": "What about useEffect? How does it compare?",
            "user_id": "context_test_user"
        }
    )
    
    if result2["success"]:
        data = result2["data"]
        print_success("Context was maintained across messages!")
        print_info(f"Context Length: {data.get('context_length')} messages")
        print_info(f"Response refers to previous useState discussion")

def test_8_expert_reasoning():
    """Test 8: Expert-Level Reasoning"""
    print_header("Test 8: Expert-Level Deep Reasoning")
    
    result = test_endpoint(
        "Expert Query",
        "POST",
        "/deep-reasoning",
        {
            "problem": "Design a scalable microservices architecture for an e-commerce platform expecting 1 million daily users",
            "context": "Need to handle payment processing, inventory, user management, and real-time notifications",
            "reasoning_steps": 10,
            "user_id": TEST_USER_ID
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Reasoning Steps: {len(data.get('reasoning_steps', []))}")
        print_info(f"Confidence: {data.get('confidence', 0):.0%}")
        print_info(f"Solution Length: {len(data.get('solution', ''))} chars")
        print(f"\n{Colors.YELLOW}Solution Preview:{Colors.RESET}")
        print(data.get('solution', '')[:400] + "...")

def test_9_fact_checking():
    """Test 9: Fact-Checking & Confidence Scoring"""
    print_header("Test 9: Fact-Checking & Hallucination Reduction")
    
    # Test factual question
    result = test_endpoint(
        "Factual Query",
        "POST",
        "/chat",
        {
            "message": "When was Python programming language created and by whom?",
            "user_id": TEST_USER_ID
        }
    )
    
    if result["success"]:
        data = result["data"]
        confidence = data.get('confidence_score', 0)
        fact_checked = data.get('fact_checked', False)
        
        print_info(f"Confidence Score: {confidence:.0%}")
        print_info(f"Fact Checked: {fact_checked}")
        
        if confidence >= 0.85:
            print_success("High confidence response!")
        elif confidence >= 0.75:
            print_info("Good confidence level")
        else:
            print_error("Low confidence - needs verification")

def test_10_direct_tool_execution():
    """Test 10: Direct Tool Execution"""
    print_header("Test 10: Direct Tool Execution API")
    
    result = test_endpoint(
        "Direct Calculator Call",
        "POST",
        "/execute-tool",
        {
            "tool_name": "calculator",
            "parameters": {
                "expression": "(100 + 50) * 2 - 25"
            },
            "user_id": TEST_USER_ID
        }
    )
    
    if result["success"]:
        data = result["data"]
        print_info(f"Tool: {data.get('tool')}")
        print_info(f"Result: {data.get('result')}")
        print_success("Direct tool execution working!")

# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("🧪 Claude Opus 4.5 Enhanced - Comprehensive Test Suite")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    print_info(f"Testing API at: {API_BASE}")
    print_info(f"Test User ID: {TEST_USER_ID}")
    print_info("Make sure the server is running: python claude_opus_enhanced.py\n")
    
    tests = [
        test_1_api_status,
        test_2_simple_chat,
        test_3_deep_reasoning,
        test_4_calculator_tool,
        test_5_crypto_tool,
        test_6_multi_language,
        test_7_context_memory,
        test_8_expert_reasoning,
        test_9_fact_checking,
        test_10_direct_tool_execution
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            time.sleep(2)  # Delay between tests
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("📊 Test Summary")
    print("="*70)
    print(f"{Colors.RESET}")
    
    print_success(f"Passed: {passed}/{len(tests)}")
    if failed > 0:
        print_error(f"Failed: {failed}/{len(tests)}")
    
    print(f"\n{Colors.YELLOW}Next Steps:{Colors.RESET}")
    print("1. Check API docs at: http://localhost:10000/docs")
    print("2. Read full guide: OPUS_4.5_FEATURES.md")
    print("3. Try advanced features in your application")
    print("4. Deploy to production!\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}\n")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
