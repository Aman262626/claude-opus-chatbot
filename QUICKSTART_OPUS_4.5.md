# ⚡ Quick Start Guide - Claude Opus 4.5 Enhanced

> Get started with advanced AI in **5 minutes**!

---

## 🚀 Installation (2 minutes)

```bash
# Clone repository
git clone https://github.com/Aman262626/claude-opus-chatbot.git
cd claude-opus-chatbot

# Install dependencies
pip install -r requirements.txt

# Run the enhanced version
python claude_opus_enhanced.py
```

**✅ Server started at:** `http://localhost:10000`

---

## 💻 Quick Test (1 minute)

### Test 1: Simple Chat

```python
import requests

API = "http://localhost:10000"

response = requests.post(f"{API}/chat", json={
    "message": "Explain machine learning in simple terms",
    "user_id": "test_user"
})

print(response.json()["response"])
```

### Test 2: Deep Reasoning

```python
response = requests.post(f"{API}/chat", json={
    "message": "Find the bug in this code: def add(a,b): return a+b print(add(5))",
    "reasoning_depth": "deep",
    "enable_tools": True
})

result = response.json()
print(f"Analysis: {result['response']}")
print(f"Confidence: {result['confidence_score']:.0%}")
```

### Test 3: Calculator Tool

```python
response = requests.post(f"{API}/chat", json={
    "message": "Calculate 25% of 10000",
    "enable_tools": True
})

print(response.json()["response"])
print("Tools used:", response.json()["tools_used"])
```

---

## 🎯 Key Features Demo

### 1. Deep Reasoning (Auto-detected)

```python
# System automatically uses DEEP reasoning for complex queries

response = requests.post(f"{API}/chat", json={
    "message": """Analyze this React component for performance issues:
    
    function UserList() {
        const [users, setUsers] = useState([]);
        useEffect(() => {
            fetchUsers().then(setUsers);
        });
        return users.map(u => <User key={u.id} data={u} />);
    }
    """
})

print(response.json()["reasoning_depth"])  # Output: "deep"
```

### 2. 200K Context Window

```python
# Can process entire codebases

with open("large_file.txt", "r") as f:
    huge_code = f.read()  # 50,000+ lines

response = requests.post(f"{API}/chat", json={
    "message": f"Analyze this codebase for security issues:\n\n{huge_code}",
    "user_id": "dev_123"
})

print(response.json()["context_length"])  # Uses up to 200K tokens
```

### 3. Vision Analysis

```python
import base64

# Read image
with open("code_screenshot.png", "rb") as f:
    img_data = base64.b64encode(f.read()).decode()

response = requests.post(f"{API}/vision", json={
    "image_base64": img_data,
    "question": "Find syntax errors in this code"
})

print(response.json()["analysis"])
```

### 4. Agentic Tools

```python
# System automatically detects and uses required tools

response = requests.post(f"{API}/chat", json={
    "message": "What's Bitcoin price and calculate 10% of it?"
})

result = response.json()
print("Tools used:", result["tools_used"])  # ["crypto_prices", "calculator"]
print(result["response"])
```

### 5. Fact-Checking

```python
response = requests.post(f"{API}/chat", json={
    "message": "When was Python created?"
})

result = response.json()
print(f"Response: {result['response']}")
print(f"Confidence: {result['confidence_score']:.0%}")
print(f"Fact-checked: {result['fact_checked']}")
```

---

## 🌐 API Endpoints

### 1. Chat (Main endpoint)
```
POST /chat

Body:
{
  "message": "Your question",
  "user_id": "optional",
  "reasoning_depth": "quick|standard|deep|expert",
  "enable_tools": true,
  "enable_vision": false,
  "image_base64": "optional"
}
```

### 2. Vision Analysis
```
POST /vision

Body:
{
  "image_base64": "<base64_image>",
  "question": "What do you see?",
  "user_id": "optional"
}
```

### 3. Deep Reasoning
```
POST /deep-reasoning

Body:
{
  "problem": "Complex problem description",
  "context": "Additional context",
  "reasoning_steps": 10,
  "user_id": "optional"
}
```

### 4. Execute Tool
```
POST /execute-tool

Body:
{
  "tool_name": "calculator",
  "parameters": {"expression": "2 + 2"}
}
```

### 5. Health Check
```
GET /health

Response:
{
  "status": "optimal",
  "active_users": 5,
  "features_status": {...}
}
```

---

## 📚 Interactive API Docs

**Swagger UI:** `http://localhost:10000/docs`

- ✅ Try all endpoints directly
- ✅ See request/response schemas
- ✅ Interactive testing
- ✅ Auto-generated examples

**ReDoc:** `http://localhost:10000/redoc`

- ✅ Beautiful documentation
- ✅ Detailed descriptions
- ✅ Code samples

---

## 🔧 Available Tools

| Tool | Auto-Trigger Keywords | Example |
|------|----------------------|----------|
| **Calculator** | calculate, compute, math, +, -, *, / | "Calculate 25% of 5000" |
| **Crypto Prices** | bitcoin, ethereum, btc, eth, crypto | "Bitcoin price in rupees?" |
| **Weather** | weather, temperature, forecast | "Weather in Mumbai" |
| **Translator** | translate, translation | "Translate hello to Hindi" |
| **Code Executor** | execute code | "Run this Python code" |
| **Web Search** | search, find, latest | "Latest AI news" |
| **Image Analyzer** | analyze image | "Describe this image" |

---

## 💡 Pro Tips

### 1. Automatic Reasoning Depth

```python
# System auto-detects complexity:

# EXPERT level (15+ second response)
"Design a distributed system architecture for real-time analytics"

# DEEP level (8-10 second response)  
"Debug this React component and optimize performance"

# STANDARD level (3-5 second response)
"Explain how React hooks work"

# QUICK level (1-2 second response)
"What is Python?"
```

### 2. Multi-Language Support

```python
# Works with Hindi, Hinglish, and 100+ languages

response = requests.post(f"{API}/chat", json={
    "message": "Machine learning kya hai aur yeh kaise kaam karta hai?"
})

# Responds fluently in Hinglish
```

### 3. Context Persistence

```python
# Use same user_id for conversation continuity

# Message 1
requests.post(f"{API}/chat", json={
    "message": "What is React?",
    "user_id": "student_123"
})

# Message 2 (remembers previous context)
requests.post(f"{API}/chat", json={
    "message": "How do I use hooks in it?",  # Knows "it" = React
    "user_id": "student_123"
})
```

### 4. Confidence Scoring

```python
# Always check confidence for critical decisions

result = response.json()
if result["confidence_score"] < 0.75:
    print("⚠️ Low confidence - verify manually")
```

---

## ❗ Common Issues

### Issue 1: Port Already in Use

```bash
# Change port
export PORT=8000
python claude_opus_enhanced.py
```

### Issue 2: Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 3: Slow Responses

- Use `reasoning_depth="quick"` for faster responses
- Enable only required tools
- Reduce conversation history by resetting periodically

---

## 🚀 Deploy to Production

### Render (Free)

1. Push to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. New Web Service
4. Connect repo: `Aman262626/claude-opus-chatbot`
5. Build: `pip install -r requirements.txt`
6. Start: `uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT`
7. Deploy!

### Heroku

```bash
heroku create your-app-name
git push heroku main
heroku open
```

### Railway

1. Visit [Railway.app](https://railway.app/)
2. New Project → Deploy from GitHub
3. Select repository
4. Auto-deploys!

---

## 📈 Next Steps

1. **Read Full Guide**: [OPUS_4.5_FEATURES.md](./OPUS_4.5_FEATURES.md)
2. **Explore API Docs**: `http://localhost:10000/docs`
3. **Try Advanced Features**: Vision analysis, deep reasoning
4. **Build Your App**: Integrate into your project
5. **Deploy**: Make it live on Render/Heroku

---

## 📞 Need Help?

- **GitHub Issues**: [Report bugs/questions](https://github.com/Aman262626/claude-opus-chatbot/issues)
- **Documentation**: [Full feature guide](./OPUS_4.5_FEATURES.md)
- **API Docs**: `/docs` endpoint

---

## ✅ Checklist

- [ ] Installed dependencies
- [ ] Started server successfully
- [ ] Tested basic chat
- [ ] Tried deep reasoning
- [ ] Tested a tool (calculator/crypto)
- [ ] Checked API docs at `/docs`
- [ ] Read full feature guide
- [ ] Deployed to production (optional)

---

**You're ready to build with Claude Opus 4.5! 🚀**

**Built with ❤️ by Aman262626**
