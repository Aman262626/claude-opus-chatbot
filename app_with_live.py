from flask import Flask, request, jsonify, Blueprint
import requests
import json
import os
import re
import base64
from datetime import datetime, timedelta
from live_conversation_module import create_live_conversation_app, transcribe_audio_whisper, synthesize_speech_google, get_live_response

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
    
    time_keywords = ['time', 'date', 'day', 'today', 'समय', 'आज']
    crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'price']
    
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

# ==================== EXISTING ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    """API status"""
    return jsonify({
        "status": "operational",
        "message": "🚀 Premium AI Platform with LIVE Conversation",
        "version": "8.0.0",
        "features": {
            "text_chat": True,
            "image_generation": True,
            "video_generation": True,
            "multi_language": True,
            "real_time_data": True,
            "conversation_memory": True,
            "live_conversation": True,  # NEW!
            "voice_chat": True,  # NEW!
            "audio_input_output": True  # NEW!
        },
        "supported_languages": list(SUPPORTED_LANGUAGES.values()),
        "endpoints": {
            "/": "API status",
            "/chat": "Intelligent chat with memory",
            "/health": "Health check",
            "/live/start": "Start live conversation session",
            "/live/audio": "Send audio for live conversation",
            "/live/text": "Send text for live conversation",
            "/live/end": "End live conversation session",
            "/live/status": "Check active live sessions"
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
            response_text = get_opus_response(user_message, conversation_history, detected_language, real_time_data)
            
            update_conversation_context(user_id, user_message, response_text, detected_language)
            
            return jsonify({
                "success": True,
                "type": "text",
                "response": response_text,
                "model_used": "opus-4.5",
                "language": SUPPORTED_LANGUAGES.get(detected_language),
                "conversation_length": conversations[user_id]["metadata"]["message_count"],
                "real_time_data_used": real_time_data is not None
            })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "optimal",
        "message": "All systems operational - Live Conversation Ready",
        "active_users": len(conversations),
        "total_conversations": sum(c["metadata"]["message_count"] for c in conversations.values()),
        "features_active": {
            "text_chat": True,
            "image_generation": True,
            "video_generation": True,
            "multi_language": True,
            "real_time_data": True,
            "conversation_memory": True,
            "live_conversation": True,
            "voice_chat": True
        },
        "timestamp": get_current_time_info()['formatted']
    })

# ==================== LIVE CONVERSATION ENDPOINTS ====================

@app.route('/live/start', methods=['POST'])
def start_live():
    """Start live conversation"""
    try:
        data = request.json or {}
        session_id = data.get('session_id', f"live_{datetime.now().timestamp()}")
        language = data.get('language', 'en')
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Live conversation session started",
            "language": language,
            "supports": {
                "voice_input": True,
                "text_input": True,
                "audio_output": True,
                "real_time": True
            },
            "endpoints": {
                "audio": "/live/audio",
                "text": "/live/text",
                "end": "/live/end",
                "status": "/live/status"
            },
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/live/audio', methods=['POST'])
def live_audio():
    """Process audio for live conversation"""
    try:
        data = request.json
        if not data or 'audio' not in data:
            return jsonify({"success": False, "error": "Audio data required"}), 400
        
        audio_base64 = data.get('audio')
        language = data.get('language', 'en')
        session_id = data.get('session_id', f"live_{datetime.now().timestamp()}")
        
        # Transcribe
        transcription = transcribe_audio_whisper(audio_base64)
        
        if not transcription['success']:
            # Fallback
            user_text = "[Audio received]"
        else:
            user_text = transcription['text']
        
        # Get response
        ai_response = get_live_response(user_text, [], language)
        
        if not ai_response['success']:
            return jsonify(ai_response), 500
        
        response_text = ai_response['response']
        
        # Convert to speech
        tts_result = synthesize_speech_google(response_text, language)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "user_input": user_text,
            "ai_response": response_text,
            "audio": tts_result.get('audio') if tts_result['success'] else None,
            "language": language,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/live/text', methods=['POST'])
def live_text():
    """Process text for live conversation"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "Message required"}), 400
        
        message = data.get('message')
        language = data.get('language', 'en')
        session_id = data.get('session_id', f"live_{datetime.now().timestamp()}")
        include_audio = data.get('include_audio', False)
        
        # Get response
        ai_response = get_live_response(message, [], language)
        
        if not ai_response['success']:
            return jsonify(ai_response), 500
        
        response_text = ai_response['response']
        audio_data = None
        
        if include_audio:
            tts_result = synthesize_speech_google(response_text, language)
            audio_data = tts_result.get('audio') if tts_result['success'] else None
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "user_input": message,
            "ai_response": response_text,
            "audio": audio_data,
            "language": language,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/live/end', methods=['POST'])
def end_live():
    """End live conversation"""
    try:
        data = request.json or {}
        session_id = data.get('session_id')
        
        return jsonify({
            "success": True,
            "message": "Live conversation session ended",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/live/status', methods=['GET'])
def live_status():
    """Get live conversation status"""
    return jsonify({
        "status": "live_conversation_ready",
        "message": "Live conversation system is operational",
        "features": {
            "voice_to_text": "Enabled",
            "text_to_speech": "Enabled",
            "real_time_response": "Enabled",
            "multi_language": "Enabled"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)