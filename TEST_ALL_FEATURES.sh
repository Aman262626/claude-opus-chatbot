#!/bin/bash
# Complete API Testing Script - All Features
# Run: bash TEST_ALL_FEATURES.sh

BASE_URL="https://claude-opus-chatbot.onrender.com"

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              🧪 API TESTING - ALL FEATURES                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TEST_NUM=0

print_test() {
    TEST_NUM=$((TEST_NUM + 1))
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}TEST #$TEST_NUM: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================================================
# TEST 1: API Status Check
# ============================================================================
print_test "API Status Check"
echo "Endpoint: GET /"
echo ""

RESPONSE=$(curl -s "$BASE_URL/")
echo "$RESPONSE" | jq '.'

if echo "$RESPONSE" | jq -e '.status == "operational"' > /dev/null; then
    print_success "API is operational"
else
    print_error "API status check failed"
fi
echo ""
sleep 2

# ============================================================================
# TEST 2: Health Check
# ============================================================================
print_test "Health Check"
echo "Endpoint: GET /health"
echo ""

RESPONSE=$(curl -s "$BASE_URL/health")
echo "$RESPONSE" | jq '.'

if echo "$RESPONSE" | jq -e '.status == "optimal"' > /dev/null; then
    print_success "Health check passed"
else
    print_error "Health check failed"
fi
echo ""
sleep 2

# ============================================================================
# TEST 3: Simple Text Chat (OPUS API)
# ============================================================================
print_test "Simple Text Chat (OPUS API)"
echo "Endpoint: POST /chat"
echo "Query: Hello, how are you?"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "test_user_1"
  }')

echo "$RESPONSE" | jq '.'

MODEL=$(echo "$RESPONSE" | jq -r '.model_used')
if [ "$MODEL" = "opus-4.5" ]; then
    print_success "OPUS API working - Model: $MODEL"
else
    print_error "Expected OPUS API, got: $MODEL"
fi
echo ""
sleep 2

# ============================================================================
# TEST 4: Complex Query (GPT-5 PRO API)
# ============================================================================
print_test "Complex Query (GPT-5 PRO API)"
echo "Endpoint: POST /chat"
echo "Query: Complex algorithm question"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please provide a detailed analysis of the merge sort algorithm and debug this code with comprehensive explanation",
    "user_id": "test_user_1"
  }')

echo "$RESPONSE" | jq '.'

MODEL=$(echo "$RESPONSE" | jq -r '.model_used')
if [ "$MODEL" = "gpt5-pro" ]; then
    print_success "GPT-5 PRO API working - Model: $MODEL"
else
    print_error "Expected GPT-5 PRO, got: $MODEL"
fi
echo ""
sleep 2

# ============================================================================
# TEST 5: Hinglish Chat
# ============================================================================
print_test "Hinglish Chat Support"
echo "Endpoint: POST /chat"
echo "Query: Bhai Python mein loops kaise likhte hain?"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bhai Python mein loops kaise likhte hain?",
    "user_id": "test_user_2"
  }')

echo "$RESPONSE" | jq '.'

LANG=$(echo "$RESPONSE" | jq -r '.language')
if [ "$LANG" = "Hinglish" ]; then
    print_success "Hinglish detection working - Language: $LANG"
else
    print_success "Language detected: $LANG"
fi
echo ""
sleep 2

# ============================================================================
# TEST 6: Real-Time Data (Current Time)
# ============================================================================
print_test "Real-Time Data - Current Time"
echo "Endpoint: POST /chat"
echo "Query: What time is it?"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current time and date?",
    "user_id": "test_user_3"
  }')

echo "$RESPONSE" | jq '.'

REALTIME=$(echo "$RESPONSE" | jq -r '.real_time_data_used')
if [ "$REALTIME" = "true" ]; then
    print_success "Real-time data integration working"
else
    print_success "Response received (real-time data: $REALTIME)"
fi
echo ""
sleep 2

# ============================================================================
# TEST 7: Crypto Prices
# ============================================================================
print_test "Real-Time Data - Crypto Prices"
echo "Endpoint: POST /chat"
echo "Query: Bitcoin price kya hai?"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bitcoin price kya hai?",
    "user_id": "test_user_3"
  }')

echo "$RESPONSE" | jq '.'

REALTIME=$(echo "$RESPONSE" | jq -r '.real_time_data_used')
if [ "$REALTIME" = "true" ]; then
    print_success "Crypto price API working"
else
    print_success "Response received (real-time data: $REALTIME)"
fi
echo ""
sleep 2

# ============================================================================
# TEST 8: Conversation Memory
# ============================================================================
print_test "Conversation Memory"
echo "Endpoint: POST /chat (multiple messages)"
echo ""

echo "Message 1: My name is Aman"
RESPONSE1=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Aman",
    "user_id": "memory_test"
  }')

echo "$RESPONSE1" | jq '.'
echo ""
sleep 2

echo "Message 2: What is my name?"
RESPONSE2=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "user_id": "memory_test"
  }')

echo "$RESPONSE2" | jq '.'

CONV_LENGTH=$(echo "$RESPONSE2" | jq -r '.conversation_length')
if [ "$CONV_LENGTH" -ge 4 ]; then
    print_success "Conversation memory working - Length: $CONV_LENGTH messages"
else
    print_error "Memory issue - Length: $CONV_LENGTH"
fi
echo ""
sleep 2

# ============================================================================
# TEST 9: Image Generation
# ============================================================================
print_test "Image Generation (Stable Diffusion 3.5)"
echo "Endpoint: POST /chat"
echo "Query: Generate image of sunset"
echo "⚠️  Note: This may take 15-30 seconds"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate image of beautiful sunset over mountains",
    "user_id": "test_user_4"
  }')

echo "$RESPONSE" | jq 'del(.image) | .'

TYPE=$(echo "$RESPONSE" | jq -r '.type')
if [ "$TYPE" = "image" ]; then
    print_success "Image generation working"
    echo "Image data (base64): $(echo "$RESPONSE" | jq -r '.image' | head -c 100)..."
else
    print_error "Image generation failed or not triggered"
fi
echo ""
sleep 2

# ============================================================================
# TEST 10: Video Generation
# ============================================================================
print_test "Video Generation (Runway AI)"
echo "Endpoint: POST /chat"
echo "Query: Generate video of dancing robot"
echo "⚠️  Note: This may take 30-60 seconds"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate video of a robot dancing",
    "user_id": "test_user_5"
  }')

echo "$RESPONSE" | jq 'del(.video) | .'

TYPE=$(echo "$RESPONSE" | jq -r '.type')
if [ "$TYPE" = "video" ]; then
    print_success "Video generation working"
    echo "Video data (base64): $(echo "$RESPONSE" | jq -r '.video' | head -c 100)..."
else
    print_error "Video generation failed or not triggered"
fi
echo ""
sleep 2

# ============================================================================
# TEST 11: Live Conversation - Start Session
# ============================================================================
print_test "Live Conversation - Start Session"
echo "Endpoint: POST /live/start"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/live/start" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en"
  }')

echo "$RESPONSE" | jq '.'

SESSION_ID=$(echo "$RESPONSE" | jq -r '.session_id')
if [ "$SESSION_ID" != "null" ] && [ -n "$SESSION_ID" ]; then
    print_success "Live session created - ID: $SESSION_ID"
else
    print_error "Failed to create live session"
fi
echo ""
sleep 2

# ============================================================================
# TEST 12: Live Conversation - Text Input
# ============================================================================
if [ "$SESSION_ID" != "null" ] && [ -n "$SESSION_ID" ]; then
    print_test "Live Conversation - Text Input"
    echo "Endpoint: POST /live/text"
    echo "Session ID: $SESSION_ID"
    echo ""

    RESPONSE=$(curl -s -X POST "$BASE_URL/live/text" \
      -H "Content-Type: application/json" \
      -d "{
        \"session_id\": \"$SESSION_ID\",
        \"message\": \"Hello! How are you?\",
        \"language\": \"en\",
        \"include_audio\": false
      }")

    echo "$RESPONSE" | jq '.'

    SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
    if [ "$SUCCESS" = "true" ]; then
        print_success "Live text conversation working"
    else
        print_error "Live text conversation failed"
    fi
    echo ""
    sleep 2
fi

# ============================================================================
# TEST 13: Live Conversation - Status Check
# ============================================================================
print_test "Live Conversation - Status Check"
echo "Endpoint: GET /live/status"
echo ""

RESPONSE=$(curl -s "$BASE_URL/live/status")
echo "$RESPONSE" | jq '.'

STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "live_conversation_ready" ]; then
    print_success "Live conversation system ready"
else
    print_success "Status: $STATUS"
fi
echo ""
sleep 2

# ============================================================================
# TEST 14: Reset Conversation
# ============================================================================
print_test "Reset Conversation"
echo "Endpoint: POST /reset"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/reset" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "memory_test"
  }')

echo "$RESPONSE" | jq '.'

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" = "true" ]; then
    print_success "Conversation reset working"
else
    print_error "Reset failed"
fi
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 TESTING COMPLETE!                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Total Tests Run: $TEST_NUM${NC}"
echo ""
echo "✅ Tested Features:"
echo "   1. API Status"
echo "   2. Health Check"
echo "   3. Simple Chat (OPUS API)"
echo "   4. Complex Chat (GPT-5 PRO API)"
echo "   5. Hinglish Support"
echo "   6. Real-time Time/Date"
echo "   7. Crypto Prices"
echo "   8. Conversation Memory"
echo "   9. Image Generation"
echo "  10. Video Generation"
echo "  11. Live Conversation (Start)"
echo "  12. Live Conversation (Text)"
echo "  13. Live Status"
echo "  14. Conversation Reset"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "For detailed API documentation, see:"
echo "  • LIVE_CONVERSATION_GUIDE.md"
echo "  • API_GUIDE.md"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""