# Free AI Chatbot API - Opus 4.5 Equivalent

🚀 **Completely FREE** AI chatbot API with Claude Opus 4.5 level responses!

## ✨ Features
- ✅ **100% FREE** - No API key needed!
- ✅ Claude Opus 4.5 equivalent responses
- ✅ Conversation history tracking
- ✅ Multiple user support
- ✅ REST API endpoints
- ✅ Easy deployment on Render
- ✅ No rate limits

## 🌐 Live Demo
Deploy kar lo aur apna URL yahan update kar do!

## 📡 API Endpoints

### GET /
Health check and API information

**Response:**
```json
{
  "status": "active",
  "message": "Free AI Chatbot API is running",
  "model": "opus-4.5-equivalent",
  "endpoints": {
    "/": "GET - API status",
    "/chat": "POST - Send message",
    "/reset": "POST - Reset conversation"
  }
}
```

### POST /chat
Send message to AI chatbot

**Request:**
```json
{
  "message": "What is artificial intelligence?",
  "user_id": "user123" // Optional, defaults to 'default'
}
```

**Response:**
```json
{
  "success": true,
  "response": "Artificial intelligence (AI) refers to...",
  "model": "opus-4.5-equivalent",
  "user_id": "user123",
  "usage": {
    "input_tokens": 5,
    "output_tokens": 150,
    "total_tokens": 155
  },
  "conversation_length": 2
}
```

### POST /reset
Reset conversation history

**Request:**
```json
{
  "user_id": "user123" // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation reset successfully. Cleared 10 messages.",
  "user_id": "user123"
}
```

### GET /health
Check API health status

**Response:**
```json
{
  "status": "healthy",
  "active_users": 5,
  "total_conversations": 125
}
```

## 🚀 Deploy on Render (FREE!)

### Step 1: Fork Repository
Fork this repository to your GitHub account.

### Step 2: Connect to Render
1. Go to [Render.com](https://render.com)
2. Sign up/Login (use GitHub for easy connection)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository: `claude-opus-chatbot`

### Step 3: Configure
- **Name**: `my-chatbot-api` (or any name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Instance Type**: **Free**

### Step 4: Deploy!
✅ **NO Environment Variables Needed!**
✅ **NO API Keys Required!**

Just click **"Create Web Service"** and you're done! 🎉

## 💻 Local Development

```bash
# Clone repository
git clone https://github.com/Aman262626/claude-opus-chatbot.git
cd claude-opus-chatbot

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

API will be available at: `http://localhost:5000`

## 📝 Usage Examples

### Python Example
```python
import requests

# Your deployed API URL
url = "https://your-app.onrender.com/chat"

# Send message
payload = {
    "message": "Explain quantum computing in simple terms",
    "user_id": "user123"
}

response = requests.post(url, json=payload)
result = response.json()

print(result['response'])
print(f"Tokens used: {result['usage']['total_tokens']}")
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

const url = 'https://your-app.onrender.com/chat';

const payload = {
  message: 'What is machine learning?',
  user_id: 'user456'
};

axios.post(url, payload)
  .then(response => {
    console.log(response.data.response);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### cURL Example
```bash
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello AI!", "user_id": "test"}'
```

### Telegram Bot Integration
```python
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

API_URL = "https://your-app.onrender.com/chat"

async def handle_message(update: Update, context):
    user_message = update.message.text
    user_id = str(update.message.from_user.id)
    
    # Call your API
    response = requests.post(API_URL, json={
        "message": user_message,
        "user_id": user_id
    })
    
    result = response.json()
    await update.message.reply_text(result['response'])

# Add to your bot
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
```

## 🎯 Features in Detail

### Conversation Memory
- API automatically tracks conversation history per user
- Use `user_id` to maintain separate conversations
- Use `/reset` endpoint to clear history

### Multiple Users
- Support for unlimited concurrent users
- Each user identified by unique `user_id`
- Independent conversation histories

### Token Tracking
- Estimates input/output tokens
- Helps monitor API usage
- No limits or restrictions

## ⚡ Performance
- Fast response times
- Auto-scaling on Render
- Handles concurrent requests
- Free tier: Sleeps after 15min inactivity

## 🔧 Troubleshooting

### API is slow
- Free tier may take 30-50 seconds to wake up
- Upgrade to paid tier for instant responses

### Getting errors
- Check request format (must be JSON)
- Ensure `message` field is not empty
- Verify API URL is correct

## 📊 API Limits
- ✅ **FREE Forever**
- ✅ No rate limits
- ✅ No API key needed
- ✅ Unlimited requests

## 🌟 Advantages

| Feature | This API | Claude Opus 4.5 |
|---------|----------|----------------|
| Cost | **FREE** | $5-25 per MTok |
| API Key | **Not Required** | Required |
| Setup Time | **1 minute** | 10+ minutes |
| Quality | High | Highest |
| Rate Limits | None | Yes |

## 🔐 Security Note
This API uses a free backend service. For production use with sensitive data, consider:
- Adding authentication
- Rate limiting
- Input validation
- Encryption

## 📄 License
MIT License - Free to use, modify, and distribute!

## 👨‍💻 Author
Created by **CodeX_Network**

## 🤝 Contributing
Pull requests are welcome! Feel free to improve this project.

## ⭐ Support
If this helped you, please star the repository!

---

**Happy Coding! 🚀**

Deploy now and get your FREE AI API in minutes!