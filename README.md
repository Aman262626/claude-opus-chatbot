# Claude Opus 4.5 Chatbot API

AI-powered chatbot using Claude Opus 4.5 by Anthropic.

## 🚀 Features
- Claude Opus 4.5 integration
- Conversation history tracking
- REST API endpoints
- Easy deployment on Render

## 📡 API Endpoints

### GET /
Health check endpoint

**Response:**
```json
{
  "status": "active",
  "message": "Claude Opus 4.5 API is running",
  "model": "claude-opus-4-5"
}
```

### POST /chat
Send message to chatbot

**Request:**
```json
{
  "message": "Your question here",
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "success": true,
  "response": "AI response here",
  "model": "claude-opus-4-5",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 50
  }
}
```

### POST /reset
Reset conversation history

**Request:**
```json
{
  "user_id": "optional_user_id"
}
```

## 🔧 Environment Variables
- `ANTHROPIC_API_KEY` - Your Anthropic API key (Required)
- `PORT` - Port number (Auto-set by Render)

## 🌐 Deployment on Render

1. Fork this repository
2. Go to [Render](https://render.com)
3. Create new Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Add Environment Variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your API key from [Anthropic Console](https://console.anthropic.com/)
7. Deploy!

## 💻 Local Development

```bash
# Clone repository
git clone https://github.com/Aman262626/claude-opus-chatbot.git
cd claude-opus-chatbot

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Run locally
python app.py
```

## 📝 Usage Examples

### Python
```python
import requests

url = "http://localhost:5000/chat"
payload = {
    "message": "What is artificial intelligence?",
    "user_id": "user123"
}

response = requests.post(url, json=payload)
print(response.json()['response'])
```

### cURL
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "user123"}'
```

## ⚠️ Important Notes
- Claude Opus 4.5 pricing: $5/MTok input, $25/MTok output
- Free Render tier sleeps after 15 minutes of inactivity
- Never commit API keys to repository
- Use environment variables for sensitive data

## 📄 License
MIT License

## 👨‍💻 Author
Created by CodeX_Network

---
⭐ Star this repo if you find it helpful!