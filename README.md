# 🚀 Triple AI API Router - Chat + Image Generation

**Intelligent Multi-Model AI API** with automatic routing for text chat and image generation powered by:
- **Opus 4.5** - Fast general queries
- **GPT-5 Pro** - Complex reasoning tasks  
- **Stable Diffusion 3.5 Large** - Professional image generation

[![Live API](https://img.shields.io/badge/Live-API-success)](https://claude-opus-chatbot-y6kx.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ Features

### 🤖 **Triple Model Support**
- **Opus 4.5** - Fast responses for general queries
- **GPT-5 Pro** - Detailed analysis, coding, research
- **Stable Diffusion 3.5 Large** - High-quality image generation

### 🧠 **Intelligent Routing**
- Automatically detects text vs image requests
- Smart model selection based on query complexity
- Context-aware conversation handling

### 🎨 **Image Generation**
- Text-to-image with Stable Diffusion 3.5 Large
- Base64 encoded output
- Natural language prompts (English + Hindi)
- Professional quality results

### 💬 **Advanced Chat**
- Conversation memory per user
- Multi-turn dialogues
- Token usage tracking
- Error handling & retries

---

## 🎯 Quick Start

### **Base URL**
```
https://claude-opus-chatbot-y6kx.onrender.com
```

### **1. Text Chat (Auto-Routing)**
```bash
curl -X POST https://claude-opus-chatbot-y6kx.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "user_id": "user123"
  }'
```

### **2. Image Generation (Auto-Detect)**
```bash
curl -X POST https://claude-opus-chatbot-y6kx.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate image of a sunset over mountains",
    "user_id": "user123"
  }'
```

### **3. Direct Image Generation**
```bash
curl -X POST https://claude-opus-chatbot-y6kx.onrender.com/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city at night with neon lights"
  }'
```

---

## 📡 API Endpoints

### **GET /** - API Status
Returns API information and available models.

```json
{
  "status": "active",
  "message": "Triple AI API Router - Chat + Image Generation",
  "models": {
    "opus-4.5": "Fast text chat",
    "gpt5-pro": "Complex text tasks",
    "stable-diffusion-3.5-large": "Image generation"
  },
  "version": "3.0"
}
```

---

### **POST /chat** - Intelligent Routing

**Auto-detects** if request is for text chat or image generation.

#### Request Body:
```json
{
  "message": "Your question or image generation prompt",
  "user_id": "unique_user_id",  // Optional, default: "default"
  "model": "opus-4.5"  // Optional: force specific model
}
```

#### Text Response:
```json
{
  "success": true,
  "type": "text",
  "response": "AI response text...",
  "model_used": "gpt5-pro",
  "user_id": "user123",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 150,
    "total_tokens": 160
  },
  "conversation_length": 4
}
```

#### Image Response:
```json
{
  "success": true,
  "type": "image",
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",  // Base64 encoded
  "format": "base64",
  "model_used": "stable-diffusion-3.5-large",
  "prompt": "sunset over mountains",
  "message": "Image generated successfully!"
}
```

---

### **POST /generate-image** - Direct Image Generation

Direct endpoint for image generation without auto-detection.

#### Request Body:
```json
{
  "prompt": "A detailed description of the image you want"
}
```

#### Response:
```json
{
  "success": true,
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",  // Base64
  "format": "base64",
  "model": "stable-diffusion-3.5-large",
  "prompt": "your prompt",
  "message": "Image generated! Decode base64 to view."
}
```

---

### **POST /chat/opus** - Force Opus 4.5

```json
{
  "message": "Quick question",
  "user_id": "user123"
}
```

---

### **POST /chat/gpt5pro** - Force GPT-5 Pro

```json
{
  "message": "Write production-ready code for...",
  "user_id": "user123"
}
```

---

### **POST /reset** - Reset Conversation

```json
{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation reset. Cleared 6 messages.",
  "user_id": "user123"
}
```

---

### **GET /health** - Health Check

```json
{
  "status": "healthy",
  "active_users": 5,
  "total_conversations": 42,
  "models": {
    "opus-4.5": "Available",
    "gpt5-pro": "Available",
    "stable-diffusion-3.5": "Available"
  }
}
```

---

## 💻 Code Examples

### **Python - Text Chat**
```python
import requests

url = "https://claude-opus-chatbot-y6kx.onrender.com/chat"

data = {
    "message": "Explain machine learning in simple terms",
    "user_id": "user123"
}

response = requests.post(url, json=data)
result = response.json()

print(result['response'])
```

### **Python - Image Generation**
```python
import requests
import base64
from PIL import Image
from io import BytesIO

url = "https://claude-opus-chatbot-y6kx.onrender.com/chat"

data = {
    "message": "Generate image of a beautiful sunset",
    "user_id": "user123"
}

response = requests.post(url, json=data)
result = response.json()

if result['type'] == 'image':
    # Decode base64 image
    image_data = base64.b64decode(result['image'])
    image = Image.open(BytesIO(image_data))
    image.save('output.png')
    print("Image saved as output.png")
```

### **JavaScript - Fetch API**
```javascript
const url = 'https://claude-opus-chatbot-y6kx.onrender.com/chat';

const data = {
  message: 'Write a Python function to sort a list',
  user_id: 'user123'
};

fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
  if (result.type === 'text') {
    console.log(result.response);
  } else if (result.type === 'image') {
    // Display base64 image
    const img = document.createElement('img');
    img.src = 'data:image/png;base64,' + result.image;
    document.body.appendChild(img);
  }
});
```

### **cURL - Direct Image Generation**
```bash
curl -X POST https://claude-opus-chatbot-y6kx.onrender.com/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A majestic lion in the African savanna at golden hour"
  }' \
  | jq -r '.image' \
  | base64 -d > image.png
```

---

## 🎨 Image Generation Examples

### **Trigger Keywords (Auto-Detection)**

The API automatically detects image generation requests using these keywords:

**English:**
- "generate image of"
- "create image of"
- "make image"
- "draw"
- "paint"
- "picture of"
- "photo of"
- "visualize"
- "illustrate"

**Hindi:**
- "बनाओ तस्वीर"
- "तस्वीर बनाओ"
- "फोटो बनाओ"
- "इमेज बनाओ"

### **Example Prompts**

```json
// Example 1: Natural scene
{
  "message": "Generate image of a peaceful forest with morning mist"
}

// Example 2: Character
{
  "message": "Create image of a futuristic robot warrior"
}

// Example 3: Abstract
{
  "message": "Paint a colorful abstract art with geometric shapes"
}

// Example 4: Hindi
{
  "message": "एक खूबसूरत पहाड़ की तस्वीर बनाओ"
}
```

---

## 🧠 Intelligent Routing Logic

### **Text Chat Model Selection**

**Opus 4.5** is selected for:
- Simple questions (who, what, when, where)
- Definitions and meanings
- Quick summaries
- General conversations
- Translation requests

**GPT-5 Pro** is selected for:
- Code writing and debugging
- Complex analysis and research
- Mathematical problems
- Technical documentation
- Step-by-step reasoning
- Long-form content (>50 words)

### **Image Generation**

Triggered when message contains image-related keywords in any language.

---

## 🔧 Installation (Local Development)

### **Prerequisites**
```bash
Python 3.9+
pip
```

### **Setup**
```bash
# Clone repository
git clone https://github.com/Aman262626/claude-opus-chatbot.git
cd claude-opus-chatbot

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

### **requirements.txt**
```txt
Flask==3.0.0
requests==2.31.0
Pillow==10.1.0
gunicorn==21.2.0
```

---

## 🌐 Deployment

### **Deploy to Render**

1. Fork this repository
2. Connect to Render
3. Create new Web Service
4. Deploy automatically

### **Environment Variables**
```bash
PORT=5000  # Auto-set by Render
```

---

## 📊 Model Comparison

| Feature | Opus 4.5 | GPT-5 Pro | Stable Diffusion 3.5 |
|---------|----------|-----------|----------------------|
| **Speed** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡⚡⚡ |
| **Quality** | 🏆🏆🏆🏆 | 🏆🏆🏆🏆🏆 | 🏆🏆🏆🏆🏆 |
| **Best For** | Quick queries | Complex tasks | Image generation |
| **Token Limit** | ~4000 | ~8000 | N/A |
| **Response Time** | 1-3s | 3-8s | 10-30s |

---

## ⚠️ Usage Limits

- **Rate Limit:** Fair usage policy
- **Image Generation:** 60 second timeout
- **Conversation History:** Per user_id
- **Image Size:** ~1MB base64 encoded

---

## 🎯 Use Cases

### **Text Chat**
✅ Customer support bots  
✅ Educational assistants  
✅ Code generation  
✅ Research assistance  
✅ Content writing  

### **Image Generation**
✅ Social media content  
✅ Marketing materials  
✅ Concept art  
✅ Product mockups  
✅ Educational illustrations  

---

## 🔐 Security

- No authentication required (public API)
- Rate limiting via Render
- No data storage (stateless)
- Base64 encoding for images
- Input validation on all endpoints

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📝 License

MIT License - Free to use for commercial and personal projects.

---

## 👨‍💻 Author

**Aman Gupta**  
GitHub: [@Aman262626](https://github.com/Aman262626)

---

## 🌟 Star History

If you find this useful, please ⭐ star the repository!

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Aman262626/claude-opus-chatbot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Aman262626/claude-opus-chatbot/discussions)

---

## 🎉 Changelog

### **v3.0** - January 2026
- ✨ Added Stable Diffusion 3.5 Large image generation
- 🧠 Intelligent text/image request detection
- 🎨 Base64 image encoding
- 🌐 Multi-language prompt support (English + Hindi)
- 📡 New `/generate-image` endpoint

### **v2.0** - December 2025
- 🤖 Added GPT-5 Pro model
- 🧠 Intelligent model routing
- 💬 Conversation history
- 📊 Token usage tracking

### **v1.0** - November 2025
- 🚀 Initial release
- 🤖 Opus 4.5 support
- 📡 Basic chat API

---

## 🚀 Roadmap

- [ ] Image-to-Image generation
- [ ] Batch processing
- [ ] Webhook support
- [ ] API key authentication
- [ ] Rate limiting dashboard
- [ ] Multi-language UI

---

**Made with ❤️ by Aman Gupta**

[![GitHub](https://img.shields.io/github/stars/Aman262626/claude-opus-chatbot?style=social)](https://github.com/Aman262626/claude-opus-chatbot)
[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://claude-opus-chatbot-y6kx.onrender.com)