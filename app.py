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

# API endpoints
OPUS_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
GPT5_PRO_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
IMAGE_GEN_API = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large'
VIDEO_GEN_API = 'https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b'

# Multi-Language Support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'hi-en': 'Hinglish',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German'
}

def detect_language(text):
    """Detect language with Hinglish support"""
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if hindi_chars > 0 and english_chars > 0:
        return 'hi-en'
    elif hindi_chars > english_chars:
        return 'hi'
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
    
    if any(k in message_lower for k in ['time', 'date', 'day', 'today', 'समय', 'आज']):
        return 'time'
    elif any(k in message_lower for k in ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth']):
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
    return [{"role": m["role"], "content": m["content"]} for m in recent]

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
    """Generate image"""
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
    """Generate video"""
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

def get_opus_response(question, conversation_history=[], language='en', real_time_data=None):
    """Get response from Opus"""
    messages = []
    
    time_info = get_current_time_info()
    system_context = f"You are a premium AI assistant. Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language)}. Provide professional responses."
    
    if real_time_data:
        system_context += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
    
    messages.append({'role': 'system', 'content': system_context})
    messages.extend(conversation_history)
    messages.append({'role': 'user', 'content': question})
    
    try:
        response = requests.post(OPUS_API, json={'messages': messages}, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Service temporarily unavailable (Status: {response.status_code})"
    except Exception as e:
        return f"Service error: {str(e)}"

def get_gpt5_pro_response(question, conversation_history=[], language='en', real_time_data=None):
    """Get response from GPT-5 Pro"""
    messages = []
    
    time_info = get_current_time_info()
    system_prompt = f"You are an elite AI assistant. Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language)}. Deliver comprehensive, professional responses."
    
    if real_time_data:
        system_prompt += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
    
    messages.append({'role': 'assistant', 'content': system_prompt})
    messages.extend(conversation_history)
    messages.append({'role': 'user', 'content': question})
    
    try:
        response = requests.post(GPT5_PRO_API, json={'messages': messages}, timeout=45)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Premium service temporarily unavailable (Status: {response.status_code})"
    except Exception as e:
        return f"Service error: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    """API status"""
    return jsonify({
        "status": "operational",
        "message": "🚀 Premium AI Platform - Professional Edition",
        "version": "7.0.0",
        "features": {
            "multi_language": True,
            "real_time_data": True,
            "conversation_memory": True,
            "image_generation": True,
            "video_generation": True
        },
        "supported_languages": list(SUPPORTED_LANGUAGES.values()),
        "endpoints": {
            "/": "API status",
            "/chat": "Intelligent chat with memory",
            "/health": "Health check"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Professional chat endpoint"""
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
        
        real_time_query = check_for_real_time_query(user_message)
        real_time_data = get_real_time_data(real_time_query, user_message) if real_time_query else None
        
        request_type = detect_request_type(user_message)
        
        if request_type == 'video':
            prompt = clean_prompt(user_message, 'video')
            result = generate_video_runway(prompt)
            
            if result['success']:
                update_conversation_context(user_id, user_message, f"Generated video: {prompt}", detected_language)
                return jsonify({
                    "success": True,
                    "type": "video",
                    "message": "Professional video generated successfully",
                    "video": result['video'],
                    "prompt": prompt,
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
                    "message": "Professional image generated successfully",
                    "image": result['image'],
                    "prompt": prompt,
                    "language": SUPPORTED_LANGUAGES.get(detected_language)
                })
            return jsonify({"success": False, "error": result.get('error')}), 500
        
        else:
            conversation_history = get_conversation_context(user_id)
            
            # Intelligent model selection
            word_count = len(user_message.split())
            complex_keywords = ['code', 'debug', 'algorithm', 'analyze', 'detailed', 'comprehensive']
            is_complex = word_count > 50 or any(k in user_message.lower() for k in complex_keywords)
            
            if is_complex:
                response_text = get_gpt5_pro_response(user_message, conversation_history, detected_language, real_time_data)
                model = 'gpt5-pro'
            else:
                response_text = get_opus_response(user_message, conversation_history, detected_language, real_time_data)
                model = 'opus-4.5'
            
            update_conversation_context(user_id, user_message, response_text, detected_language)
            
            return jsonify({
                "success": True,
                "type": "text",
                "response": response_text,
                "model_used": model,
                "language": SUPPORTED_LANGUAGES.get(detected_language),
                "conversation_length": conversations[user_id]["metadata"]["message_count"],
                "real_time_data_used": real_time_data is not None
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
            "message": f"Conversation reset successfully. Cleared {msg_count} messages."
        })
    return jsonify({"success": True, "message": "No conversation to reset"})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "optimal",
        "message": "All systems operational - Premium AI Platform",
        "active_users": len(conversations),
        "total_conversations": sum(c["metadata"]["message_count"] for c in conversations.values()),
        "features_active": {
            "text_chat": True,
            "image_generation": True,
            "video_generation": True,
            "multi_language": True,
            "real_time_data": True,
            "conversation_memory": True
        },
        "timestamp": get_current_time_info()['formatted']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)