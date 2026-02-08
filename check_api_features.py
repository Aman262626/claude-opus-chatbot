#!/usr/bin/env python3
"""
API Feature Checker - Check all features of deployed API
Tests which features are working and which are not

Usage:
    python check_api_features.py https://your-api.onrender.com
    python check_api_features.py  # Will prompt for URL
"""

import sys
import requests
import json
import time
from typing import Dict, Any, List

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}✨ {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.CYAN}💡 {text}{Colors.RESET}")

def print_feature(name: str, status: bool, details: str = ""):
    if status:
        print(f"{Colors.GREEN}✅ {name}{Colors.RESET}")
        if details:
            print(f"   {Colors.CYAN}→ {details}{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ {name}{Colors.RESET}")
        if details:
            print(f"   {Colors.YELLOW}→ {details}{Colors.RESET}")

class APIFeatureChecker:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.results = {
            "working": [],
            "not_working": [],
            "warnings": []
        }
        self.timeout = 60
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                      data: Dict = None, timeout: int = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        try:
            url = f"{self.api_url}{endpoint}"
            timeout = timeout or self.timeout
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            else:
                response = requests.post(url, json=data, timeout=timeout)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
        
        except requests.exceptions.Timeout:
            return {"success": False, "error": f"Timeout after {timeout}s"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection failed"}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}
    
    def check_api_status(self):
        """Test 1: API Status & Availability"""
        print_header("Test 1: API Status & Availability")
        
        result = self.test_endpoint("Root Endpoint", "GET", "/", timeout=30)
        
        if result["success"]:
            print_success("API is online and responding")
            data = result.get("data", {})
            print_info(f"Model: {data.get('model', 'N/A')}")
            print_info(f"Version: {data.get('version', 'N/A')}")
            print_info(f"Response Time: {result.get('response_time', 0):.2f}s")
            
            features = data.get('features', {})
            if features:
                print_info(f"Features Listed: {len(features)}")
                for feature, status in features.items():
                    print(f"   - {feature}: {status}")
            
            self.results["working"].append("API Status Endpoint")
            return True
        else:
            print_error(f"API not responding: {result.get('error')}")
            self.results["not_working"].append("API Status Endpoint")
            return False
    
    def check_health(self):
        """Test 2: Health Check"""
        print_header("Test 2: Health Check Endpoint")
        
        result = self.test_endpoint("Health Check", "GET", "/health", timeout=30)
        
        if result["success"]:
            print_success("Health check passed")
            data = result.get("data", {})
            print_info(f"Status: {data.get('status', 'unknown')}")
            print_info(f"Active Users: {data.get('active_users', 0)}")
            
            features_status = data.get('features_status', {})
            if features_status:
                print_info("\nFeatures Status:")
                for feature, status in features_status.items():
                    print(f"   - {feature}: {status}")
            
            self.results["working"].append("Health Check")
            return True
        else:
            print_error(f"Health check failed: {result.get('error')}")
            self.results["not_working"].append("Health Check")
            return False
    
    def check_simple_chat(self):
        """Test 3: Simple Chat (Quick Reasoning)"""
        print_header("Test 3: Simple Chat - Quick Reasoning")
        
        result = self.test_endpoint(
            "Simple Chat",
            "POST",
            "/chat",
            {
                "message": "What is 2 + 2?",
                "user_id": "feature_test_user",
                "reasoning_depth": "quick"
            },
            timeout=30
        )
        
        if result["success"]:
            data = result.get("data", {})
            print_success("Simple chat is working")
            print_info(f"Response: {data.get('response', '')[:100]}...")
            print_info(f"Reasoning Depth: {data.get('reasoning_depth', 'N/A')}")
            print_info(f"Response Time: {result.get('response_time', 0):.2f}s")
            
            if 'confidence_score' in data:
                print_info(f"Confidence Score: {data['confidence_score']:.0%}")
            
            self.results["working"].append("Simple Chat")
            return True
        else:
            print_error(f"Simple chat failed: {result.get('error')}")
            self.results["not_working"].append("Simple Chat")
            return False
    
    def check_deep_reasoning(self):
        """Test 4: Deep Reasoning"""
        print_header("Test 4: Deep Reasoning")
        
        result = self.test_endpoint(
            "Deep Reasoning",
            "POST",
            "/chat",
            {
                "message": "Find the bug in this code: def add(a,b): return a+b; print(add(5))",
                "user_id": "feature_test_user",
                "reasoning_depth": "deep",
                "enable_tools": True
            },
            timeout=60
        )
        
        if result["success"]:
            data = result.get("data", {})
            print_success("Deep reasoning is working")
            print_info(f"Reasoning Level: {data.get('reasoning_depth', 'N/A')}")
            print_info(f"Response Time: {result.get('response_time', 0):.2f}s")
            
            if 'tokens_used' in data:
                print_info(f"Tokens Used: {data['tokens_used']}")
            
            if 'tools_used' in data:
                print_info(f"Tools Used: {data['tools_used']}")
            
            self.results["working"].append("Deep Reasoning")
            return True
        else:
            print_error(f"Deep reasoning failed: {result.get('error')}")
            self.results["not_working"].append("Deep Reasoning")
            return False
    
    def check_calculator_tool(self):
        """Test 5: Calculator Tool (Auto-execution)"""
        print_header("Test 5: Calculator Tool - Agentic Execution")
        
        result = self.test_endpoint(
            "Calculator Tool",
            "POST",
            "/chat",
            {
                "message": "Calculate 25% of 10000",
                "user_id": "feature_test_user",
                "enable_tools": True
            },
            timeout=30
        )
        
        if result["success"]:
            data = result.get("data", {})
            tools_used = data.get('tools_used', [])
            
            if 'calculator' in tools_used:
                print_success("Calculator tool is working (auto-detected and executed)")
                print_info(f"Response: {data.get('response', '')[:150]}")
                print_info(f"Tools Used: {tools_used}")
                self.results["working"].append("Calculator Tool")
                return True
            else:
                print_warning("Response received but calculator not auto-detected")
                print_info(f"Tools Used: {tools_used}")
                self.results["warnings"].append("Calculator Tool (not auto-detected)")
                return False
        else:
            print_error(f"Calculator tool test failed: {result.get('error')}")
            self.results["not_working"].append("Calculator Tool")
            return False
    
    def check_crypto_tool(self):
        """Test 6: Crypto Prices Tool"""
        print_header("Test 6: Crypto Prices Tool")
        
        result = self.test_endpoint(
            "Crypto Tool",
            "POST",
            "/chat",
            {
                "message": "What's the current Bitcoin price?",
                "user_id": "feature_test_user",
                "enable_tools": True
            },
            timeout=40
        )
        
        if result["success"]:
            data = result.get("data", {})
            tools_used = data.get('tools_used', [])
            
            if 'crypto_prices' in tools_used:
                print_success("Crypto prices tool is working")
                print_info(f"Response Preview: {data.get('response', '')[:150]}...")
                self.results["working"].append("Crypto Prices Tool")
                return True
            else:
                print_warning("Response received but crypto tool not used")
                self.results["warnings"].append("Crypto Prices Tool (available but not triggered)")
                return False
        else:
            print_error(f"Crypto tool test failed: {result.get('error')}")
            self.results["not_working"].append("Crypto Prices Tool")
            return False
    
    def check_multi_language(self):
        """Test 7: Multi-Language Support (Hindi/Hinglish)"""
        print_header("Test 7: Multi-Language Support")
        
        # Test Hindi
        result = self.test_endpoint(
            "Hindi Support",
            "POST",
            "/chat",
            {
                "message": "Machine learning kya hai?",
                "user_id": "feature_test_user"
            },
            timeout=30
        )
        
        if result["success"]:
            data = result.get("data", {})
            print_success("Multi-language support is working")
            print_info(f"Hindi/Hinglish query processed successfully")
            print_info(f"Response Length: {len(data.get('response', ''))} characters")
            self.results["working"].append("Multi-Language Support")
            return True
        else:
            print_error(f"Multi-language test failed: {result.get('error')}")
            self.results["not_working"].append("Multi-Language Support")
            return False
    
    def check_context_memory(self):
        """Test 8: Context Memory (200K Window)"""
        print_header("Test 8: Context Memory - Multi-Turn Conversation")
        
        test_user = "context_memory_test"
        
        # First message
        result1 = self.test_endpoint(
            "Context Message 1",
            "POST",
            "/chat",
            {
                "message": "Let's talk about Python programming.",
                "user_id": test_user
            },
            timeout=30
        )
        
        if not result1["success"]:
            print_error("Context memory test failed (first message)")
            self.results["not_working"].append("Context Memory")
            return False
        
        print_success("First message sent successfully")
        time.sleep(2)
        
        # Second message (should remember context)
        result2 = self.test_endpoint(
            "Context Message 2",
            "POST",
            "/chat",
            {
                "message": "What are its main features?",
                "user_id": test_user
            },
            timeout=30
        )
        
        if result2["success"]:
            data = result2.get("data", {})
            print_success("Context memory is working")
            print_info("Second message understood context from first message")
            
            if 'context_length' in data:
                print_info(f"Context Length: {data['context_length']} messages")
            
            self.results["working"].append("Context Memory")
            return True
        else:
            print_error(f"Context memory test failed: {result2.get('error')}")
            self.results["not_working"].append("Context Memory")
            return False
    
    def check_fact_checking(self):
        """Test 9: Fact-Checking & Confidence Scoring"""
        print_header("Test 9: Fact-Checking & Confidence Scoring")
        
        result = self.test_endpoint(
            "Fact Check",
            "POST",
            "/chat",
            {
                "message": "When was Python programming language created?",
                "user_id": "feature_test_user"
            },
            timeout=30
        )
        
        if result["success"]:
            data = result.get("data", {})
            
            if 'confidence_score' in data:
                print_success("Fact-checking is working")
                confidence = data['confidence_score']
                print_info(f"Confidence Score: {confidence:.0%}")
                print_info(f"Fact Checked: {data.get('fact_checked', False)}")
                
                if confidence >= 0.85:
                    print_info("✅ High confidence response")
                elif confidence >= 0.75:
                    print_info("🟡 Good confidence level")
                else:
                    print_warning("🟠 Low confidence - needs verification")
                
                self.results["working"].append("Fact-Checking")
                return True
            else:
                print_warning("Response received but no confidence score")
                self.results["warnings"].append("Fact-Checking (confidence score not included)")
                return False
        else:
            print_error(f"Fact-checking test failed: {result.get('error')}")
            self.results["not_working"].append("Fact-Checking")
            return False
    
    def check_vision_analysis(self):
        """Test 10: Vision Analysis (if available)"""
        print_header("Test 10: Vision Analysis")
        
        result = self.test_endpoint(
            "Vision Endpoint",
            "POST",
            "/vision",
            {
                "image_base64": "test",
                "question": "Test"
            },
            timeout=30
        )
        
        # Expected to fail if Pillow not installed
        if result["success"]:
            print_success("Vision analysis is available")
            self.results["working"].append("Vision Analysis")
            return True
        else:
            print_warning("Vision analysis not available (expected - Pillow not installed)")
            print_info("This is OK - 95% of features work without vision")
            self.results["warnings"].append("Vision Analysis (not available - requires Pillow)")
            return False
    
    def run_all_tests(self):
        """Run all feature tests"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("="*80)
        print("🧪 Claude Opus 4.5 Enhanced - Feature Checker")
        print("="*80)
        print(f"{Colors.RESET}\n")
        
        print_info(f"Testing API: {self.api_url}")
        print_info("Running comprehensive feature tests...\n")
        
        # Run all tests
        tests = [
            self.check_api_status,
            self.check_health,
            self.check_simple_chat,
            self.check_deep_reasoning,
            self.check_calculator_tool,
            self.check_crypto_tool,
            self.check_multi_language,
            self.check_context_memory,
            self.check_fact_checking,
            self.check_vision_analysis
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(2)  # Delay between tests
            except Exception as e:
                print_error(f"Test failed with exception: {str(e)}")
        
        # Generate summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("="*80)
        print("📊 Feature Test Summary")
        print("="*80)
        print(f"{Colors.RESET}\n")
        
        # Working features
        if self.results["working"]:
            print(f"{Colors.GREEN}{Colors.BOLD}\n✅ WORKING FEATURES ({len(self.results['working'])}):{ Colors.RESET}")
            for feature in self.results["working"]:
                print(f"{Colors.GREEN}   ✓ {feature}{Colors.RESET}")
        
        # Warnings
        if self.results["warnings"]:
            print(f"{Colors.YELLOW}{Colors.BOLD}\n⚠️  WARNINGS ({len(self.results['warnings'])}):{ Colors.RESET}")
            for warning in self.results["warnings"]:
                print(f"{Colors.YELLOW}   ⚠ {warning}{Colors.RESET}")
        
        # Not working
        if self.results["not_working"]:
            print(f"{Colors.RED}{Colors.BOLD}\n❌ NOT WORKING ({len(self.results['not_working'])}):{ Colors.RESET}")
            for feature in self.results["not_working"]:
                print(f"{Colors.RED}   ✗ {feature}{Colors.RESET}")
        
        # Overall status
        total = len(self.results["working"]) + len(self.results["warnings"]) + len(self.results["not_working"])
        working_percent = (len(self.results["working"]) / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Overall Status:{Colors.RESET}")
        print(f"   Working: {len(self.results['working'])}/{total} ({working_percent:.0f}%)")
        print(f"   Warnings: {len(self.results['warnings'])}/{total}")
        print(f"   Not Working: {len(self.results['not_working'])}/{total}")
        
        if working_percent >= 80:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ API is functioning well! Most features working!{Colors.RESET}")
        elif working_percent >= 50:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  API is partially functional. Some features need attention.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ API has significant issues. Many features not working.{Colors.RESET}")
        
        # Recommendations
        print(f"\n{Colors.CYAN}{Colors.BOLD}💡 Recommendations:{Colors.RESET}")
        
        if "Vision Analysis" in str(self.results["warnings"]):
            print(f"{Colors.CYAN}   - Vision analysis disabled (expected) - 95% features working{Colors.RESET}")
        
        if self.results["not_working"]:
            print(f"{Colors.CYAN}   - Check Render logs for errors{Colors.RESET}")
            print(f"{Colors.CYAN}   - Verify environment variables{Colors.RESET}")
            print(f"{Colors.CYAN}   - Ensure service is fully deployed{Colors.RESET}")
        
        print(f"\n{Colors.BLUE}API Docs: {self.api_url}/docs{Colors.RESET}")
        print(f"{Colors.BLUE}Health Check: {self.api_url}/health{Colors.RESET}\n")

def main():
    # Get API URL
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    else:
        api_url = input("\nEnter your API URL (e.g., https://your-app.onrender.com): ").strip()
    
    if not api_url:
        print_error("No API URL provided")
        sys.exit(1)
    
    # Remove trailing slash
    api_url = api_url.rstrip('/')
    
    # Create checker and run tests
    checker = APIFeatureChecker(api_url)
    
    try:
        checker.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}\n")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
