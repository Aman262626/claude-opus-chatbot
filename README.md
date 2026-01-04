# 🚀 Advanced Multi-Modal AI API

**Version 5.0** - Complete AI Platform with Chat, Image/Video Generation & File Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### **Multi-Modal AI Capabilities**
- ✅ **Text Chat** - Opus 4.5 & GPT-5 Pro models
- ✅ **Image Generation** - Stable Diffusion 3.5 Large
- ✅ **Video Generation** - Runway Gen-3 Style (Text-to-Video)
- ✅ **Image Analysis** - Deep AI-powered analysis with Gemini Flash
- ✅ **PDF Extraction** - Extract text from PDF documents
- ✅ **Word Document Analysis** - DOCX file processing
- ✅ **Spreadsheet Analysis** - Excel & CSV data analysis
- ✅ **Intelligent Routing** - Auto-detects request type

## 📋 Table of Contents

- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Supported File Types](#supported-file-types)
- [Deployment](#deployment)
- [Error Handling](#error-handling)

## 🔧 Installation

### **Prerequisites**
- Python 3.10 or higher
- pip package manager

### **Clone Repository**
```bash
git clone https://github.com/Aman262626/claude-opus-chatbot.git
cd claude-opus-chatbot
```

### **Install Dependencies**
```bash
pip install -r requirements.txt
```

## 🔑 Environment Setup

### **Required Environment Variable**

For file analysis features, you need a **free** Google Gemini API key:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### **Get Free Gemini API Key**

1. Visit: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Add to environment variables

**Free Tier Limits:**
- 15 requests per minute
- 1500 requests per day
- No credit card required

### **For Production (Render/Heroku/Railway)**

Add environment variable in platform settings:
```
GEMINI_API_KEY = your_api_key_here
```

## 🌐 API Endpoints

### **Base URL**
```
http://localhost:5000  (local)
https://your-app.onrender.com  (production)
```

### **1. Home - API Status**
```http
GET /
```

**Response:**
```json
{
  "status": "active",
  "version": "5.0",
  "models": {
    "opus-4.5": "Fast text chat",
    "gpt5-pro": "Complex text tasks",
    "stable-diffusion-3.5-large": "Image generation",
    "runway-gen-3-style": "Video generation",
    "gemini-1.5-flash": "File & Image analysis"
  }
}
```

### **2. Intelligent Chat**
```http
POST /chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Explain quantum computing",
  "user_id": "user123",
  "model": "gpt5-pro"  // optional: opus-4.5 or gpt5-pro
}
```

**Response:**
```json
{
  "success": true,
  "type": "text",
  "response": "Quantum computing is...",
  "model_used": "gpt5-pro",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 150
  }
}
```

### **3. Image Generation**
```http
POST /generate-image
Content-Type: application/json
```

**Request:**
```json
{
  "prompt": "A futuristic city at sunset"
}
```

**Response:**
```json
{
  "success": true,
  "image": "base64_encoded_image",
  "format": "base64",
  "model": "stable-diffusion-3.5-large"
}
```

### **4. Video Generation** 🆕
```http
POST /generate-video
Content-Type: application/json
```

**Request:**
```json
{
  "prompt": "A cat running in a park",
  "duration": 3  // 1-10 seconds
}
```

**Response:**
```json
{
  "success": true,
  "video": "base64_encoded_video",
  "format": "base64",
  "model": "runway-gen-3-style",
  "duration": 3,
  "fps": 8
}
```

### **5. File Analysis** 🆕
```http
POST /analyze-file
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: File to analyze (required)
- `question`: Custom question (optional)

**Example (curl):**
```bash
curl -X POST http://localhost:5000/analyze-file \
  -F "file=@document.pdf" \
  -F "question=Summarize the key points"
```

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_type": "document",
  "extracted_text": "Document content...",
  "analysis": "Key points: 1. ...",
  "model_used": "gemini-1.5-flash"
}
```

### **6. Image Analysis** 🆕
```http
POST /analyze-image
Content-Type: multipart/form-data
```

**Parameters:**
- `image`: Image file (required)
- `question`: Analysis question (optional)

**Example:**
```bash
curl -X POST http://localhost:5000/analyze-image \
  -F "image=@xray.jpg" \
  -F "question=What problems do you see?"
```

**Response:**
```json
{
  "success": true,
  "analysis": "The X-ray shows...",
  "image_info": {
    "filename": "xray.jpg",
    "format": "JPEG",
    "size": [1024, 768]
  },
  "model_used": "gemini-1.5-flash"
}
```

### **7. Text Extraction** 🆕
```http
POST /extract-text
Content-Type: multipart/form-data
```

**Example:**
```bash
curl -X POST http://localhost:5000/extract-text \
  -F "file=@contract.pdf"
```

**Response:**
```json
{
  "success": true,
  "filename": "contract.pdf",
  "text": "Extracted text content...",
  "text_length": 5000,
  "word_count": 850
}
```

### **8. Reset Conversation**
```http
POST /reset
Content-Type: application/json
```

**Request:**
```json
{
  "user_id": "user123"
}
```

### **9. Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "active_users": 5,
  "models": {
    "opus-4.5": "Available",
    "gpt5-pro": "Available",
    "gemini-1.5-flash": "Available"
  }
}
```

## 📄 Supported File Types

### **Images**
- PNG, JPG, JPEG, GIF, BMP, WEBP
- Max size: 50MB
- AI-powered analysis with Gemini

### **Documents**
- **PDF** - Text extraction & analysis
- **DOCX** - Word document processing
- **TXT** - Plain text files

### **Spreadsheets**
- **XLSX/XLS** - Excel files
- **CSV** - Comma-separated values
- Automatic statistical analysis

## 💻 Usage Examples

### **Python Example**

```python
import requests
import json
import base64

# Base URL
API_URL = "http://localhost:5000"

# 1. Text Chat
def chat(message):
    response = requests.post(f"{API_URL}/chat", json={
        "message": message,
        "user_id": "user123"
    })
    return response.json()

# 2. Generate Image
def generate_image(prompt):
    response = requests.post(f"{API_URL}/generate-image", json={
        "prompt": prompt
    })
    data = response.json()
    
    # Decode base64 image
    if data['success']:
        img_data = base64.b64decode(data['image'])
        with open('output.png', 'wb') as f:
            f.write(img_data)
    return data

# 3. Analyze Image
def analyze_image(image_path, question):
    files = {'image': open(image_path, 'rb')}
    data = {'question': question}
    response = requests.post(f"{API_URL}/analyze-image", 
                           files=files, data=data)
    return response.json()

# 4. Analyze PDF
def analyze_pdf(pdf_path, question):
    files = {'file': open(pdf_path, 'rb')}
    data = {'question': question}
    response = requests.post(f"{API_URL}/analyze-file", 
                           files=files, data=data)
    return response.json()

# 5. Extract Text from PDF
def extract_text(pdf_path):
    files = {'file': open(pdf_path, 'rb')}
    response = requests.post(f"{API_URL}/extract-text", files=files)
    return response.json()

# Usage
if __name__ == "__main__":
    # Chat example
    result = chat("Explain AI in simple terms")
    print(result['response'])
    
    # Image generation
    generate_image("A beautiful sunset")
    
    # Image analysis
    analysis = analyze_image("test.jpg", "What's in this image?")
    print(analysis['analysis'])
    
    # PDF analysis
    pdf_result = analyze_pdf("document.pdf", "Summarize this")
    print(pdf_result['analysis'])
```

### **JavaScript Example**

```javascript
const API_URL = 'http://localhost:5000';

// 1. Text Chat
async function chat(message) {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, user_id: 'user123' })
  });
  return await response.json();
}

// 2. Analyze File
async function analyzeFile(file, question) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('question', question);
  
  const response = await fetch(`${API_URL}/analyze-file`, {
    method: 'POST',
    body: formData
  });
  return await response.json();
}

// 3. Generate Image
async function generateImage(prompt) {
  const response = await fetch(`${API_URL}/generate-image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  const data = await response.json();
  
  // Decode base64 image
  if (data.success) {
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${data.image}`;
    document.body.appendChild(img);
  }
  return data;
}

// Usage
chat("Hello AI").then(result => console.log(result.response));
```

### **cURL Examples**

```bash
# 1. Text Chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test"}'

# 2. Generate Image
curl -X POST http://localhost:5000/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset"}'

# 3. Analyze Image
curl -X POST http://localhost:5000/analyze-image \
  -F "image=@photo.jpg" \
  -F "question=What's in this image?"

# 4. Analyze PDF
curl -X POST http://localhost:5000/analyze-file \
  -F "file=@document.pdf" \
  -F "question=Summarize the content"

# 5. Extract Text
curl -X POST http://localhost:5000/extract-text \
  -F "file=@document.pdf"

# 6. Health Check
curl http://localhost:5000/health
```

## 🚀 Deployment

### **Local Deployment**

```bash
# Set environment variable
export GEMINI_API_KEY="your_key_here"

# Run application
python app.py

# Server starts at http://localhost:5000
```

### **Render Deployment**

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Web Service"
4. Connect GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     - `GEMINI_API_KEY` = your_api_key
6. Click "Create Web Service"

### **Heroku Deployment**

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variable
heroku config:set GEMINI_API_KEY=your_key_here

# Deploy
git push heroku main

# Open app
heroku open
```

### **Railway Deployment**

1. Visit [Railway.app](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub"
3. Select repository
4. Add environment variable: `GEMINI_API_KEY`
5. Deploy automatically

## ⚠️ Error Handling

### **Common Errors**

**1. Gemini API Not Configured**
```json
{
  "analysis": "Gemini API key not configured. Set GEMINI_API_KEY environment variable."
}
```
**Solution:** Set `GEMINI_API_KEY` environment variable

**2. File Too Large**
```json
{
  "error": "File size exceeds 50MB limit"
}
```
**Solution:** Compress file or use smaller files

**3. Unsupported File Type**
```json
{
  "error": "File type not supported"
}
```
**Solution:** Use supported formats (PNG, JPG, PDF, DOCX, XLSX, CSV)

**4. Model Loading (Video Generation)**
```json
{
  "success": false,
  "error": "Model loading",
  "retry_after": 30
}
```
**Solution:** Wait 20-30 seconds and retry

## 📊 API Response Codes

- `200` - Success
- `400` - Bad Request (missing parameters)
- `500` - Server Error
- `503` - Service Unavailable (model loading)

## 🔒 Security Notes

- Store API keys in environment variables
- Never commit API keys to GitHub
- Use HTTPS in production
- Implement rate limiting for public APIs
- Validate all file uploads

## 🎯 Use Cases

### **Medical Analysis**
- X-ray interpretation
- Medical report analysis
- Symptom documentation

### **Document Processing**
- Contract summarization
- Legal document analysis
- Research paper extraction

### **Data Analysis**
- Excel report analysis
- CSV data insights
- Statistical summaries

### **Creative Content**
- Image generation
- Video creation
- Story writing

## 📈 Performance

- **Chat Response**: ~1-3 seconds
- **Image Generation**: ~5-10 seconds
- **Video Generation**: ~30-60 seconds
- **File Analysis**: ~2-5 seconds
- **PDF Extraction**: ~1-3 seconds

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

MIT License - Free to use for personal and commercial projects

## 📧 Support

For issues or questions:
- Create GitHub Issue
- Check documentation
- Review examples

## 🌟 Star This Repo!

If you find this useful, please give it a ⭐️!

---

**Built with ❤️ by Aman262626**

**Version**: 5.0  
**Last Updated**: January 2026  
**Status**: Active Development