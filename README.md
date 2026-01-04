# 🤖 Intelligent Dual AI API Router

**Free AI API** with automatic intelligent routing between **Opus 4.5** and **GPT-5 Pro** equivalent models!

## ✨ Revolutionary Features

- 🧠 **Intelligent Auto-Routing** - Automatically selects best model for your query
- ⚡ **Dual Model Support** - Opus 4.5 (fast) + GPT-5 Pro (complex)
- 🎯 **Smart Detection** - Analyzes query complexity and routes accordingly
- 💰 **100% FREE** - No API key needed!
- 🔄 **Conversation Memory** - Maintains context across messages
- 🚀 **Production Ready** - Deploy on Render in 2 minutes

## 🎯 How It Works

### Intelligent Routing System

API **automatically detects** query type and selects best model:

#### **GPT-5 Pro Equivalent** triggers for:
- 💻 **Coding tasks**: algorithms, debugging, development
- 🔬 **Research & Analysis**: scientific, academic work
- 🧮 **Complex reasoning**: math, logic, proofs
- 📊 **Professional tasks**: legal, medical, financial
- 📝 **Long-form content**: essays, reports, documentation

#### **Opus 4.5 Equivalent** triggers for:
- 💬 **General conversation**: greetings, simple questions
- ❓ **Quick answers**: definitions, explanations
- 📚 **Basic info**: "what is", "who is", "where is"
- ⚡ **Fast queries**: summaries, translations

## 📡 API Endpoints

### 🎯 Main Endpoint (Auto-Routing)

#### POST /chat
Intelligently routes to best model automatically

**Request:**
```json
{
  "message": "Write a Python function to calculate fibonacci",
  "user_id": "user123"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "response": "Here's an optimized Python function...",
  "model_used": "gpt5-pro",
  "user_id": "user123",
  "usage": {
    "input_tokens": 8,
    "output_tokens": 150,
    "total_tokens": 158
  },
  "conversation_length": 2,
  "routing_info": {
    "auto_selected": true,
    "reason": "Intelligent query analysis"
  }
}
```

### 🎨 Force Specific Model

#### POST /chat/opus
Force Opus 4.5 equivalent (fast responses)

#### POST /chat/gpt5pro
Force GPT-5 Pro equivalent (detailed responses)

**Request (same format):**
```json
{
  "message": "Your question",
  "user_id": "user123"
}
```

### 🔄 Other Endpoints

#### GET /
API status and information

#### POST /reset
Reset conversation history
```json
{
  "user_id": "user123"
}
```

#### GET /health
Health check and statistics

## 🚀 Deploy on Render (FREE!)

### Quick Deploy (2 Minutes)

1. **Fork this repo** to your GitHub

2. **Go to [Render.com](https://render.com)**
   - Sign up/Login with GitHub

3. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect `claude-opus-chatbot` repository

4. **Configure (Auto-filled)**
   ```
   Name: ai-router-api
   Environment: Python 3
   Build: pip install -r requirements.txt
   Start: gunicorn app:app
   Instance: Free
   ```

5. **Deploy!**
   - ✅ No API keys needed
   - ✅ No environment variables
   - Just click "Create Web Service"

## 💻 Usage Examples

### Python Example
```python
import requests

url = "https://your-app.onrender.com/chat"

# Example 1: Coding (Auto-routes to GPT-5 Pro)
payload = {
    "message": "Create a REST API with Flask for user authentication",
    "user_id": "dev123"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Model used: {result['model_used']}")  # gpt5-pro
print(result['response'])

# Example 2: Simple question (Auto-routes to Opus 4.5)
payload = {
    "message": "What is Python?",
    "user_id": "dev123"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Model used: {result['model_used']}")  # opus-4.5
print(result['response'])
```

### Force Specific Model
```python
# Force GPT-5 Pro for detailed response
url = "https://your-app.onrender.com/chat/gpt5pro"
payload = {"message": "Explain quantum computing"}

# Force Opus 4.5 for quick response
url = "https://your-app.onrender.com/chat/opus"
payload = {"message": "What is AI?"}
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const url = 'https://your-app.onrender.com/chat';

// Coding task - Auto-routes to GPT-5 Pro
const codingQuery = {
  message: 'Write a sorting algorithm in JavaScript',
  user_id: 'js_dev'
};

axios.post(url, codingQuery)
  .then(res => {
    console.log('Model:', res.data.model_used);
    console.log('Response:', res.data.response);
  });
```

### cURL
```bash
# Auto-routing
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Debug this Python code", "user_id": "test"}'

# Force GPT-5 Pro
curl -X POST https://your-app.onrender.com/chat/gpt5pro \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze this algorithm complexity"}'
```

## 🎯 Routing Intelligence Examples

| Query | Detected Model | Reason |
|-------|----------------|--------|
| "Write a Python function" | **GPT-5 Pro** | Coding task |
| "Debug my code" | **GPT-5 Pro** | Technical/complex |
| "Research paper on AI" | **GPT-5 Pro** | Research task |
| "Calculate fibonacci" | **GPT-5 Pro** | Algorithm |
| "Hello, how are you?" | **Opus 4.5** | General chat |
| "What is Python?" | **Opus 4.5** | Simple definition |
| "Summarize this" | **Opus 4.5** | Quick task |
| "Translate to Hindi" | **Opus 4.5** | Fast operation |

## 🔥 Advanced Features

### Conversation Context
```python
# All messages maintain context per user_id
url = "https://your-app.onrender.com/chat"

# Message 1
requests.post(url, json={
    "message": "My name is Aman",
    "user_id": "aman123"
})

# Message 2 - Remembers context
response = requests.post(url, json={
    "message": "What's my name?",
    "user_id": "aman123"
})
# Response: "Your name is Aman"
```

### Reset Conversation
```python
requests.post("https://your-app.onrender.com/reset", json={
    "user_id": "aman123"
})
```

### Health Monitoring
```python
response = requests.get("https://your-app.onrender.com/health")
print(response.json())
# {
#   "status": "healthy",
#   "active_users": 10,
#   "total_conversations": 150,
#   "models": {"opus-4.5": "Available", "gpt5-pro": "Available"}
# }
```

## 🎨 Integration Examples

### Telegram Bot
```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import requests

API_URL = "https://your-app.onrender.com/chat"

async def handle_message(update: Update, context):
    user_msg = update.message.text
    user_id = str(update.message.from_user.id)
    
    response = requests.post(API_URL, json={
        "message": user_msg,
        "user_id": user_id
    })
    
    result = response.json()
    model_emoji = "🚀" if result['model_used'] == 'gpt5-pro' else "⚡"
    
    await update.message.reply_text(
        f"{model_emoji} {result['response']}\n\n"
        f"Model: {result['model_used']}"
    )
```

### Discord Bot
```python
import discord
import requests

API_URL = "https://your-app.onrender.com/chat"

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    response = requests.post(API_URL, json={
        "message": message.content,
        "user_id": str(message.author.id)
    })
    
    result = response.json()
    await message.channel.send(
        f"**{result['model_used'].upper()}**: {result['response']}"
    )
```

## 📊 Performance

| Feature | Opus 4.5 | GPT-5 Pro |
|---------|----------|----------|
| **Speed** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ |
| **Quality** | 🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| **Use Case** | General, Fast | Complex, Detailed |
| **Response Time** | 1-3 seconds | 3-10 seconds |
| **Best For** | Chat, Quick info | Code, Analysis |

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/Aman262626/claude-opus-chatbot.git
cd claude-opus-chatbot

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Access at: `http://localhost:5000`

## 🎯 Why This API?

### ✅ Advantages
- **Smart Routing** - Best model for each query
- **No API Keys** - Zero setup hassle
- **Free Forever** - No hidden costs
- **Context Memory** - Natural conversations
- **Production Ready** - Stable and reliable
- **Multi-Model** - Best of both worlds

### 🆚 Comparison

| Feature | This API | Claude Official | OpenAI Official |
|---------|----------|-----------------|----------------|
| Cost | **FREE** | $3-25/MTok | $1-120/MTok |
| API Key | **Not Needed** | Required | Required |
| Auto-Routing | **Yes** | No | No |
| Models | **2 Models** | 3 Models | 10+ Models |
| Setup Time | **1 min** | 10 min | 10 min |

## 🚨 Important Notes

- Free tier sleeps after 15min inactivity (30-50s wake time)
- For production, consider paid tier for instant responses
- No rate limits on free version
- Supports unlimited concurrent users

## 📄 License
MIT License - Free to use and modify!

## 👨‍💻 Author
Created by **CodeX_Network**

## 🤝 Contributing
Pull requests welcome! Improve the routing algorithm or add features.

## ⭐ Support
If this helped you, please **star the repository**!

---

## 🎉 Quick Start Summary

1. ✅ Fork this repo
2. ✅ Deploy on Render (2 minutes)
3. ✅ No API keys needed
4. ✅ Start using immediately!

**Deploy now and get your intelligent AI router in minutes!** 🚀

---

**Happy Coding!** 🎯