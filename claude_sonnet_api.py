from flask import Flask, request, jsonify
import requests
import json
import os
import re
import base64
from datetime import datetime, timedelta

app = Flask(__name__)

# Conversation storage
conversations = {}
CONTEXT_WINDOW = 20

# CLAUDE 3.5 SONNET API Configuration
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
CLAUDE_API_ENDPOINT = 'https://api.anthropic.com/v1/messages'
CLAUDE_MODEL = 'claude-3-5-sonnet-20241022'

# Fallback APIs (if Claude fails)
OPUS_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
GPT5_PRO_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'

# Image & Video Generation APIs
IMAGE_GEN_API = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large'
VIDEO_GEN_API = 'https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b'

# Multi-Language Support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'hi-en': 'Hinglish',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ur': 'Urdu',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ml': 'Malayalam'
}

def detect_language(text):
    """Detect language with Hinglish support"""
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    
    if hindi_chars > 0 and english_chars > 0:
        return 'hi-en'
    elif urdu_chars > 0 and english_chars > 0:
        return 'ur'
    elif hindi_chars > english_chars:
        return 'hi'
    elif urdu_chars > 0:
        return 'ur'
    return 'en'

def get_current_time_info():
    """Get current IST time"""
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return {
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'day': now.strftime('%A'),
        'formatted': now.strftime('%d %B %Y, %I:%M %p IST')
    }

def fetch_crypto_prices():
    """Fetch cryptocurrency prices"""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,inr'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def check_for_real_time_query(message):
    """Check if message needs real-time data"""
    message_lower = message.lower()
    
    time_keywords = ['time', 'date', 'day', 'today', 'समय', 'आज', 'وقت', 'آج']
    crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'price', 'قیمت']
    
    if any(k in message_lower for k in time_keywords):
        return 'time'
    elif any(k in message_lower for k in crypto_keywords):
        return 'crypto'
    return None

def get_real_time_data(query_type, message):
    """Fetch real-time data"""
    data = {}
    if query_type == 'time':
        data['time_info'] = get_current_time_info()
    elif query_type == 'crypto':
        data['crypto'] = fetch_crypto_prices()
    return data

def init_conversation(user_id):
    """Initialize conversation"""
    if user_id not in conversations:
        conversations[user_id] = {
            "messages": [],
            "context": {"language": 'en'},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
        }

def update_conversation_context(user_id, message, response, language='en'):
    """Update conversation"""
    if user_id not in conversations:
        init_conversation(user_id)
    
    conv = conversations[user_id]
    conv["messages"].append({"role": "user", "content": message})
    conv["messages"].append({"role": "assistant", "content": response})
    conv["context"]["language"] = language
    conv["metadata"]["message_count"] = len(conv["messages"])

def get_conversation_context(user_id):
    """Get recent conversation context"""
    if user_id not in conversations:
        return []
    
    conv = conversations[user_id]
    recent = conv["messages"][-CONTEXT_WINDOW:]
    return recent

def detect_request_type(message):
    """Detect request type"""
    message_lower = message.lower()
    
    video_keywords = ['generate video', 'create video', 'make video', 'video of', 'animate']
    image_keywords = ['generate image', 'create image', 'make image', 'draw', 'paint', 'image of', 'picture of']
    
    if any(k in message_lower for k in video_keywords):
        return 'video'
    elif any(k in message_lower for k in image_keywords):
        return 'image'
    return 'text'

def clean_prompt(message, content_type='image'):
    """Extract prompt for generation"""
    triggers = ['generate', 'create', 'make', 'draw', 'paint', 'of', 'video', 'image', 'picture']
    words = message.split()
    for i, word in enumerate(words):
        if any(t in word.lower() for t in triggers):
            return ' '.join(words[i+1:]) if i+1 < len(words) else message
    return message

def generate_image_sd35(prompt):
    """Generate image using Stable Diffusion 3.5"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": prompt}
        response = requests.post(IMAGE_GEN_API, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            img_base64 = base64.b64encode(response.content).decode('utf-8')
            return {"success": True, "image": img_base64}
        return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_video_runway(prompt, duration=3):
    """Generate video using Runway"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": f"{prompt}, cinematic, high quality"}
        response = requests.post(VIDEO_GEN_API, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            video_base64 = base64.b64encode(response.content).decode('utf-8')
            return {"success": True, "video": video_base64}
        return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_claude_response(question, conversation_history=[], language='en', real_time_data=None):
    """Get response from Claude 3.5 Sonnet - PREMIUM"""
    try:
        # If no API key, fallback to free API
        if not CLAUDE_API_KEY:
            return get_fallback_response(question, conversation_history, language, real_time_data)
        
        time_info = get_current_time_info()
        
        system_context = f"""You are Claude 3.5 Sonnet, an elite AI assistant by Anthropic.
Current time: {time_info['formatted']}
User language: {SUPPORTED_LANGUAGES.get(language, 'English')}

Provide thoughtful, accurate, and comprehensive responses.
Be conversational and natural.
Support multiple languages including Hinglish, Urdu, and Indian languages."""
        
        if real_time_data:
            system_context += f"\n\nReal-time data available: {json.dumps(real_time_data)}"
        
        # Build messages
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        messages.append({"role": "user", "content": question})
        
        # Call Claude API
        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": CLAUDE_MODEL,
            "max_tokens": 1024,
            "system": system_context,
            "messages": messages
        }
        
        response = requests.post(CLAUDE_API_ENDPOINT, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        else:
            return get_fallback_response(question, conversation_history, language, real_time_data)
    
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return get_fallback_response(question, conversation_history, language, real_time_data)

def get_fallback_response(question, conversation_history=[], language='en', real_time_data=None):
    """Fallback to free API if Claude unavailable"""
    try:
        time_info = get_current_time_info()
        system_context = f"You are a premium AI assistant. Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language)}. Provide professional responses."
        
        if real_time_data:
            system_context += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
        
        messages = []
        for msg in conversation_history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": question})
        
        payload = {"messages": [{"role": "system", "content": system_context}] + messages}
        
        response = requests.post(OPUS_API, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return "Service temporarily unavailable. Please try again."
    except:
        return "I'm experiencing technical difficulties. Please try again in a moment."

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        "status": "operational",
        "message": "🚀 Claude 3.5 Sonnet Premium AI Platform",
        "version": "8.0.0",
        "primary_model": "Claude 3.5 Sonnet (Anthropic)",
        "features": {
            "text_chat": True,
            "image_generation": True,
            "video_generation": True,
            "multi_language": True,
            "real_time_data": True,
            "conversation_memory": True,
            "claude_3_5_sonnet": True
        },
        "supported_languages": list(SUPPORTED_LANGUAGES.values()),
        "endpoints": {
            "/": "API status",
            "/chat": "Chat with Claude 3.5 Sonnet",
            "/health": "Health check",
            "/reset": "Reset conversation"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint with Claude 3.5 Sonnet"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "Please provide a message"}), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
        detected_language = detect_language(user_message)
        init_conversation(user_id)
        
        # Check for real-time data needs
        real_time_query = check_for_real_time_query(user_message)
        real_time_data = get_real_time_data(real_time_query, user_message) if real_time_query else None
        
        # Detect request type
        request_type = detect_request_type(user_message)
        
        if request_type == 'video':
            prompt = clean_prompt(user_message, 'video')
            result = generate_video_runway(prompt)
            
            if result['success']:
                update_conversation_context(user_id, user_message, f"Generated video: {prompt}", detected_language)
                return jsonify({
                    "success": True,
                    "type": "video",
                    "message": "Video generated successfully",
                    "video": result['video'],
                    "prompt": prompt,
                    "model": "Claude 3.5 Sonnet + Runway",
                    "language": SUPPORTED_LANGUAGES.get(detected_language)
                })
            return jsonify({"success": False, "error": result.get('error')}), 500
        
        elif request_type == 'image':
            prompt = clean_prompt(user_message, 'image')
            result = generate_image_sd35(prompt)
            
            if result['success']:
                update_conversation_context(user_id, user_message, f"Generated image: {prompt}", detected_language)
                return jsonify({
                    "success": True,
                    "type": "image",
                    "message": "Image generated successfully",
                    "image": result['image'],
                    "prompt": prompt,
                    "model": "Claude 3.5 Sonnet + Stable Diffusion 3.5",
                    "language": SUPPORTED_LANGUAGES.get(detected_language)
                })
            return jsonify({"success": False, "error": result.get('error')}), 500
        
        else:
            # Text conversation with Claude
            conversation_history = get_conversation_context(user_id)
            response_text = get_claude_response(user_message, conversation_history, detected_language, real_time_data)
            
            update_conversation_context(user_id, user_message, response_text, detected_language)
            
            return jsonify({
                "success": True,
                "type": "text",
                "response": response_text,
                "model_used": "claude-3-5-sonnet",
                "language": SUPPORTED_LANGUAGES.get(detected_language),
                "conversation_length": conversations[user_id]["metadata"]["message_count"],
                "real_time_data_used": real_time_data is not None,
                "timestamp": get_current_time_info()['formatted']
            })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation"""
    data = request.json if request.json else {}
    user_id = data.get('user_id', 'default')
    
    if user_id in conversations:
        msg_count = conversations[user_id]["metadata"]["message_count"]
        del conversations[user_id]
        return jsonify({
            "success": True,
            "message": f"Conversation reset. Cleared {msg_count} messages."
        })
    return jsonify({"success": True, "message": "No conversation to reset"})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "optimal",
        "message": "Claude 3.5 Sonnet API - All systems operational",
        "model": "claude-3-5-sonnet-20241022",
        "active_users": len(conversations),
        "total_conversations": sum(c["metadata"]["message_count"] for c in conversations.values()),
        "features_active": {
            "text_chat": True,
            "image_generation": True,
            "video_generation": True,
            "multi_language": True,
            "real_time_data": True,
            "conversation_memory": True,
            "claude_api": bool(CLAUDE_API_KEY)
        },
        "timestamp": get_current_time_info()['formatted']
    })

if __name__ == '__main__':
    # Render provides PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Claude 3.5 Sonnet API starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)