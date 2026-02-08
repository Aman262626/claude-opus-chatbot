#!/usr/bin/env python3
"""
Deployment Verification Script
Verifies that your deployed API is working correctly

Usage:
    python verify_deployment.py https://your-app.onrender.com
"""

import sys
import requests
import time
from typing import Dict, Any

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}✨ {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.YELLOW}💡 {text}{Colors.RESET}")

def verify_endpoint(name: str, url: str, method: str = "GET", data: Dict = None, timeout: int = 30) -> bool:
    """
    Verify a single endpoint
    """
    try:
        print(f"\n{Colors.YELLOW}Testing: {name}{Colors.RESET}")
        print(f"URL: {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=data, timeout=timeout)
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code} OK")
            
            # Show response preview
            try:
                json_data = response.json()
                if isinstance(json_data, dict):
                    for key in list(json_data.keys())[:3]:  # First 3 keys
                        print_info(f"{key}: {str(json_data[key])[:50]}...")
            except:
                print_info(f"Response: {response.text[:100]}...")
            
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    
    except requests.exceptions.Timeout:
        print_error(f"Timeout after {timeout} seconds")
        return False
    except requests.exceptions.ConnectionError:
        print_error("Connection failed - Check if service is running")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """
    Main verification function
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("🚀 Claude Opus 4.5 - Deployment Verification")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    # Get API URL
    if len(sys.argv) < 2:
        print_error("Please provide your API URL")
        print(f"\nUsage: python verify_deployment.py <API_URL>")
        print(f"Example: python verify_deployment.py https://your-app.onrender.com\n")
        sys.exit(1)
    
    api_base = sys.argv[1].rstrip('/')
    
    print_info(f"API Base URL: {api_base}")
    print_info("Starting verification...\n")
    
    tests = []
    passed = 0
    failed = 0
    
    # Test 1: Root endpoint
    print_header("Test 1: Root Endpoint")
    result = verify_endpoint(
        "Root Endpoint",
        f"{api_base}/",
        method="GET"
    )
    tests.append(("Root Endpoint", result))
    if result:
        passed += 1
    else:
        failed += 1
    
    time.sleep(2)
    
    # Test 2: Health check
    print_header("Test 2: Health Check")
    result = verify_endpoint(
        "Health Check",
        f"{api_base}/health",
        method="GET"
    )
    tests.append(("Health Check", result))
    if result:
        passed += 1
    else:
        failed += 1
    
    time.sleep(2)
    
    # Test 3: Simple chat
    print_header("Test 3: Chat Endpoint (Simple)")
    result = verify_endpoint(
        "Simple Chat",
        f"{api_base}/chat",
        method="POST",
        data={
            "message": "Hello! Is the API working?",
            "user_id": "deployment_test"
        },
        timeout=30
    )
    tests.append(("Simple Chat", result))
    if result:
        passed += 1
    else:
        failed += 1
    
    time.sleep(2)
    
    # Test 4: Tool execution
    print_header("Test 4: Tool Execution (Calculator)")
    result = verify_endpoint(
        "Calculator Tool",
        f"{api_base}/chat",
        method="POST",
        data={
            "message": "Calculate 2 + 2",
            "enable_tools": True
        },
        timeout=30
    )
    tests.append(("Calculator Tool", result))
    if result:
        passed += 1
    else:
        failed += 1
    
    time.sleep(2)
    
    # Test 5: Deep reasoning
    print_header("Test 5: Deep Reasoning")
    result = verify_endpoint(
        "Deep Reasoning",
        f"{api_base}/chat",
        method="POST",
        data={
            "message": "Explain quantum computing in simple terms",
            "reasoning_depth": "deep"
        },
        timeout=45
    )
    tests.append(("Deep Reasoning", result))
    if result:
        passed += 1
    else:
        failed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("📊 Verification Summary")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    for test_name, test_result in tests:
        if test_result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print_success(f"Passed: {passed}/{len(tests)}")
    if failed > 0:
        print_error(f"Failed: {failed}/{len(tests)}")
    
    # Overall status
    print(f"\n{Colors.BOLD}Overall Status:{Colors.RESET}")
    if passed == len(tests):
        print_success("✅ ALL TESTS PASSED - Deployment Successful! 🎉")
        print(f"\n{Colors.GREEN}Your API is live and working correctly!{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Next Steps:{Colors.RESET}")
        print(f"1. API Documentation: {api_base}/docs")
        print(f"2. ReDoc: {api_base}/redoc")
        print(f"3. Share your API with your team")
        print(f"4. Integrate with your applications\n")
    elif passed > 0:
        print_error("⚠️ PARTIAL SUCCESS - Some tests failed")
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("1. Check Render logs for errors")
        print("2. Verify environment variables")
        print("3. Ensure all dependencies installed")
        print("4. Check build logs in Render dashboard\n")
    else:
        print_error("❌ ALL TESTS FAILED - Deployment has issues")
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("1. Verify service is running in Render dashboard")
        print("2. Check build logs for errors")
        print("3. Ensure correct start command")
        print("4. Verify requirements.txt is complete")
        print(f"5. Visit: {api_base}/health to check status\n")
    
    # Exit code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verification interrupted by user{Colors.RESET}\n")
        sys.exit(1)
    except Exception as e:
        print_error(f"Verification error: {str(e)}")
        sys.exit(1)
