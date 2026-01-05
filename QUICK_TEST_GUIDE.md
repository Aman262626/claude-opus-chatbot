# 🧪 QUICK TEST GUIDE - All Features

## 🚀 3 Ways to Test Your API

### Option 1: Automated Testing (Recommended)

#### Python Script (Best for detailed testing)
```bash
python test_all_features.py
```

#### Bash Script (Best for CI/CD)
```bash
bash TEST_ALL_FEATURES.sh
```

### Option 2: Manual Testing (Use curl commands below)

### Option 3: Browser Testing (Postman/Thunder Client)

---

## 📋 MANUAL TESTING - Copy & Paste Commands

### ✅ TEST 1: API Status

```bash
curl https://claude-opus-chatbot.onrender.com/
```

**Expected Response:**
```json
{
  "status": "operational",
  "version": "7.0.0"
}
```

---

### ✅ TEST 2: Health Check

```bash
curl https://claude-opus-chatbot.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "optimal",
  "features_active": {
    "text_chat": true,
    "image_generation": true,
    "video_generation": true
  }
}
```

---

### ✅ TEST 3: Simple Chat (OPUS API)

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "test_user_1"
  }'
```

**Expected:**
- `"model_used": "opus-4.5"`
- Fast response (< 2 seconds)

---

### ✅ TEST 4: Complex Chat (GPT-5 PRO API)

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please analyze this algorithm in detail and debug the code comprehensively",
    "user_id": "test_user_1"
  }'
```

**Expected:**
- `"model_used": "gpt5-pro"`
- Detailed response

---

### ✅ TEST 5: Hinglish Support

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bhai Python mein loops kaise likhte hain?",
    "user_id": "test_user_2"
  }'
```

**Expected:**
- `"language": "Hinglish"`
- Response in Hinglish

---

### ✅ TEST 6: Real-Time Time/Date

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current time and date?",
    "user_id": "test_user_3"
  }'
```

**Expected:**
- `"real_time_data_used": true`
- Current IST time in response

---

### ✅ TEST 7: Crypto Prices

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bitcoin price kya hai?",
    "user_id": "test_user_3"
  }'
```

**Expected:**
- `"real_time_data_used": true`
- Live Bitcoin price in response

---

### ✅ TEST 8: Conversation Memory

**Step 1:**
```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Aman",
    "user_id": "memory_test"
  }'
```

**Step 2:**
```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "user_id": "memory_test"
  }'
```

**Expected:**
- Response should say "Aman"
- `"conversation_length": 4` (or more)

---

### ✅ TEST 9: Image Generation

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate image of beautiful sunset over mountains",
    "user_id": "test_user_4"
  }'
```

**Expected:**
- `"type": "image"`
- Base64 encoded image in response
- Takes 15-30 seconds

---

### ✅ TEST 10: Video Generation

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate video of a robot dancing",
    "user_id": "test_user_5"
  }'
```

**Expected:**
- `"type": "video"`
- Base64 encoded video in response
- Takes 30-60 seconds

---

### ✅ TEST 11: Live Conversation - Start Session

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/live/start \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

**Expected:**
```json
{
  "success": true,
  "session_id": "live_xxxxx"
}
```

**Save the `session_id` for next tests!**

---

### ✅ TEST 12: Live Conversation - Text Input

```bash
# Replace SESSION_ID with actual ID from TEST 11
curl -X POST https://claude-opus-chatbot.onrender.com/live/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "message": "Hello! How are you?",
    "language": "en",
    "include_audio": false
  }'
```

**Expected:**
- `"success": true`
- `"response": "...AI response..."`

---

### ✅ TEST 13: Live Conversation - Status

```bash
curl https://claude-opus-chatbot.onrender.com/live/status
```

**Expected:**
```json
{
  "status": "live_conversation_ready"
}
```

---

### ✅ TEST 14: Reset Conversation

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/reset \
  -H "Content-Type: application/json" \
  -d '{"user_id": "memory_test"}'
```

**Expected:**
```json
{
  "success": true,
  "message": "Conversation reset successfully"
}
```

---

## 🔥 QUICK 1-MINUTE TEST

Test sabse important features in 60 seconds:

```bash
# 1. Status check (2 sec)
curl https://claude-opus-chatbot.onrender.com/

# 2. Simple chat (5 sec)
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "quick_test"}'

# 3. Hinglish (5 sec)
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bhai kaise ho?", "user_id": "quick_test"}'

# 4. Real-time data (5 sec)
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bitcoin price?", "user_id": "quick_test"}'
```

**Total time: ~20 seconds**

---

## 📊 TEST RESULTS CHECKLIST

Mark these as you test:

- [ ] API Status (operational)
- [ ] Health Check (optimal)
- [ ] Simple Chat (OPUS API - model: opus-4.5)
- [ ] Complex Chat (GPT-5 PRO - model: gpt5-pro)
- [ ] Hinglish (language: Hinglish)
- [ ] Real-time Time (real_time_data_used: true)
- [ ] Crypto Prices (real_time_data_used: true)
- [ ] Conversation Memory (remembers previous messages)
- [ ] Image Generation (type: image, base64 data)
- [ ] Video Generation (type: video, base64 data)
- [ ] Live Start (session_id created)
- [ ] Live Text (response received)
- [ ] Live Status (live_conversation_ready)
- [ ] Reset (success: true)

---

## ⚡ TROUBLESHOOTING

### Issue: "Service temporarily unavailable"
**Solution:** API might be cold (sleeping on Render free tier)
- Wait 30 seconds
- Retry request

### Issue: Image/Video generation timeout
**Solution:** Increase timeout
```bash
curl --max-time 120 ...
```

### Issue: No response
**Solution:** Check API status first
```bash
curl https://claude-opus-chatbot.onrender.com/health
```

### Issue: "Model not switching to GPT-5 PRO"
**Solution:** Make query more complex
- Use 50+ words
- Include keywords: "code", "debug", "algorithm", "analyze", "detailed"

---

## 📝 TESTING TIPS

### 1. Use Different user_id for Each Test
```json
{"user_id": "test_1"}  // For simple chat
{"user_id": "test_2"}  // For Hinglish
{"user_id": "test_3"}  // For real-time
```

### 2. Pretty Print JSON (with jq)
```bash
curl ... | jq '.'
```

### 3. Save Response to File
```bash
curl ... > response.json
```

### 4. Test with Python
```python
import requests

response = requests.post(
    "https://claude-opus-chatbot.onrender.com/chat",
    json={"message": "Hello!", "user_id": "test"}
)
print(response.json())
```

---

## 🎯 EXPECTED PERFORMANCE

| Feature | Response Time |
|---------|---------------|
| API Status | < 500ms |
| Health Check | < 500ms |
| Simple Chat | 800ms - 2s |
| Complex Chat | 1.5s - 3s |
| Hinglish | 1s - 2s |
| Real-time Data | 1s - 2s |
| Image Gen | 15-30s |
| Video Gen | 30-60s |
| Live Start | < 1s |
| Live Text | 3-6s |

---

## 🔗 USEFUL LINKS

- **API URL:** https://claude-opus-chatbot.onrender.com
- **GitHub Repo:** https://github.com/Aman262626/claude-opus-chatbot
- **Full Guide:** [LIVE_CONVERSATION_GUIDE.md](LIVE_CONVERSATION_GUIDE.md)
- **Python Script:** [test_all_features.py](test_all_features.py)
- **Bash Script:** [TEST_ALL_FEATURES.sh](TEST_ALL_FEATURES.sh)

---

## ✅ TESTING COMPLETE!

If all tests pass:
```
✅ API is fully operational
✅ All 8 APIs working
✅ All features tested
✅ Ready for production
```

If any test fails:
1. Check [troubleshooting](#-troubleshooting)
2. Review [LIVE_CONVERSATION_GUIDE.md](LIVE_CONVERSATION_GUIDE.md)
3. Open GitHub issue if problem persists

---

**Happy Testing! 🎉**