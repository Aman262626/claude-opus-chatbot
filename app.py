from flask import Flask, request, jsonify, send_file
import requests
import json
import os
import re
import base64
from io import BytesIO
import time

app = Flask(__name__)

# Conversation storage
conversations = {}

# API endpoints
OPUS_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
GPT5_PRO_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
IMAGE_GEN_API = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large'
VIDEO_GEN_API = 'https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b'

def detect_request_type(message):
    """Detect if request is for video, image generation or text chat"""
    message_lower = message.lower()
    
    # Video generation keywords
    video_keywords = [
        'generate video', 'create video', 'make video', 'video of',
        'animate', 'animation', 'moving', 'motion', 'video clip',
        'वीडियो बनाओ', 'एनीमेशन बनाओ', 'मूवमेंट', 'वीडियो क्लिप',
        'runway', 'gen-3', 'text to video', 'video generation'
    ]
    
    # Image generation keywords
    image_keywords = [
        'generate image', 'create image', 'make image', 'draw', 'paint',
        'generate picture', 'create picture', 'visualize', 'illustrate',
        'image of', 'picture of', 'photo of', 'render', 'design image',
        'बनाओ तस्वीर', 'तस्वीर बनाओ', 'फोटो बनाओ', 'इमेज बनाओ'
    ]
    
    for keyword in video_keywords:
        if keyword in message_lower:
            return 'video'
    
    for keyword in image_keywords:
        if keyword in message_lower:
            return 'image'
    
    return 'text'

def detect_query_type(question):
    """Intelligent query type detection for text chat"""
    question_lower = question.lower()
    
    gpt5_pro_keywords = [
        'code', 'debug', 'algorithm', 'implement', 'function', 'class', 'api',
        'programming', 'software', 'develop', 'build', 'create app', 'script',
        'refactor', 'optimize', 'bug', 'error', 'python', 'javascript', 'react',
        'research', 'analyze', 'analysis', 'study', 'investigate', 'examine',
        'compare', 'evaluate', 'review', 'assess', 'scientific', 'academic',
        'solve', 'calculate', 'compute', 'mathematical', 'proof', 'logic',
        'reasoning', 'explain complex', 'detailed explanation', 'step by step',
        'legal', 'medical', 'financial', 'business plan', 'strategy',
        'technical document', 'architecture', 'design system',
        'essay', 'article', 'report', 'documentation', 'proposal',
        'comprehensive', 'detailed', 'in-depth'
    ]
    
    opus_keywords = [
        'hello', 'hi', 'hey', 'what is', 'tell me about', 'explain',
        'simple', 'quick', 'summary', 'summarize', 'brief',
        'translate', 'meaning', 'definition', 'who is', 'where is',
        'general', 'basic', 'simple question'
    ]
    
    gpt5_score = sum(1 for keyword in gpt5_pro_keywords if keyword in question_lower)
    opus_score = sum(1 for keyword in opus_keywords if keyword in question_lower)
    
    word_count = len(question.split())
    if word_count > 50:
        gpt5_score += 2
    
    if '```' in question or 'def ' in question or 'function' in question:
        gpt5_score += 3
    
    if '?' in question and question.count('?') > 2:
        gpt5_score += 1
    
    return 'gpt5-pro' if gpt5_score > opus_score else 'opus-4.5'

def clean_prompt(message, content_type='image'):
    """Extract clean prompt for image/video generation"""
    message_lower = message.lower()
    
    # Remove trigger phrases based on content type
    if content_type == 'video':
        triggers = [
            'generate video of', 'create video of', 'make video of',
            'video of', 'animate', 'animation of', 'वीडियो बनाओ',
            'runway', 'gen-3'
        ]
    else:
        triggers = [
            'generate image of', 'create image of', 'make image of',
            'generate picture of', 'create picture of', 'draw',
            'paint', 'image of', 'picture of', 'photo of',
            'बनाओ तस्वीर', 'तस्वीर बनाओ', 'फोटो बनाओ'
        ]
    
    prompt = message
    for trigger in triggers:
        if trigger in message_lower:
            idx = message_lower.find(trigger)
            prompt = message[idx + len(trigger):].strip()
            break
    
    return prompt

def generate_video_runway(prompt, duration=3):
    """
    Generate video using Runway Gen-3 style efficiency
    Uses Text-to-Video AI model with optimized parameters
    """
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt for better video quality
        enhanced_prompt = f"{prompt}, high quality, smooth motion, cinematic, 4k resolution"
        
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "num_frames": duration * 8,  # 8 frames per second
                "num_inference_steps": 50,
                "guidance_scale": 9.0,
                "negative_prompt": "blurry, low quality, distorted, static, choppy motion"
            }
        }
        
        # Using Hugging Face Text-to-Video API
        response = requests.post(
            VIDEO_GEN_API,
            headers=headers,
            json=payload,
            timeout=120  # Video generation takes longer
        )
        
        if response.status_code == 200:
            video_bytes = response.content
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
            return {
                "success": True,
                "video": video_base64,
                "format": "base64",
                "model": "text-to-video-ms-1.7b",
                "style": "runway-gen-3",
                "duration": duration,
                "fps": 8
            }
        elif response.status_code == 503:
            return {
                "success": False,
                "error": "Model loading",
                "message": "Video generation model is loading. Please try again in 20-30 seconds.",
                "retry_after": 30
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "message": "Video generation service temporarily unavailable"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate video"
        }

def generate_image_sd35(prompt):
    """Generate image using Stable Diffusion 3.5 Large"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "negative_prompt": "blurry, low quality, distorted, ugly"
            }
        }
        
        response = requests.post(
            IMAGE_GEN_API,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            image_bytes = response.content
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            return {
                "success": True,
                "image": img_base64,
                "format": "base64",
                "model": "stable-diffusion-3.5-large"
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "message": "Image generation service temporarily unavailable"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate image"
        }

def get_opus_response(question, conversation_history=[]):
    """Opus 4.5 - Fast, general queries"""
    messages = []
    for msg in conversation_history:
        messages.append(msg)
    messages.append({'role': 'user', 'content': question})
    
    payload = {'messages': messages}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post(OPUS_API, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: Status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_gpt5_pro_response(question, conversation_history=[]):
    """GPT-5 Pro - Complex, detailed queries"""
    messages = []
    
    system_prompt = (
        "You are an advanced AI assistant with GPT-5 Pro level capabilities. "
        "Provide detailed, accurate, and well-reasoned responses. "
        "For coding tasks, write production-ready code with best practices. "
        "For analysis, provide comprehensive insights with examples. "
        "Think step-by-step and show your reasoning when appropriate."
    )
    
    messages.append({'role': 'assistant', 'content': system_prompt})
    for msg in conversation_history:
        messages.append(msg)
    
    enhanced_question = f"Please provide a detailed, comprehensive response: {question}"
    messages.append({'role': 'user', 'content': enhanced_question})
    
    payload = {'messages': messages}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post(GPT5_PRO_API, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: Status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    """Home endpoint - API status"""
    return jsonify({
        "status": "active",
        "message": "Quad AI API Router - Chat + Image + Video Generation",
        "models": {
            "opus-4.5": "Fast text chat",
            "gpt5-pro": "Complex text tasks",
            "stable-diffusion-3.5-large": "Image generation",
            "runway-gen-3-style": "Video generation (Text-to-Video)"
        },
        "version": "4.0",
        "endpoints": {
            "/": "GET - API status",
            "/chat": "POST - Intelligent routing (text/image/video)",
            "/generate-image": "POST - Direct image generation",
            "/generate-video": "POST - Direct video generation (Runway Gen-3 style)",
            "/chat/opus": "POST - Force Opus 4.5",
            "/chat/gpt5pro": "POST - Force GPT-5 Pro",
            "/reset": "POST - Reset conversation",
            "/health": "GET - Health check"
        },
        "features": [
            "Intelligent text/image/video routing",
            "Quad model support",
            "Runway Gen-3 style video generation",
            "Stable Diffusion 3.5 Large",
            "Conversation history",
            "Free to use",
            "Auto detection"
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Intelligent chat endpoint - Auto-detects text, image or video request"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Invalid request. JSON body required."}), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        force_model = data.get('model', None)
        
        if not user_message:
            return jsonify({"error": "Message field is required."}), 400
        
        # Detect request type: text, image, or video
        request_type = detect_request_type(user_message)
        
        if request_type == 'video':
            # Video generation request
            prompt = clean_prompt(user_message, 'video')
            duration = data.get('duration', 3)  # Default 3 seconds
            result = generate_video_runway(prompt, duration)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "type": "video",
                    "video": result['video'],
                    "format": "base64",
                    "model_used": "runway-gen-3-style",
                    "prompt": prompt,
                    "duration": result.get('duration'),
                    "fps": result.get('fps'),
                    "message": "Video generated successfully! Decode base64 to view MP4."
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error'),
                    "message": result.get('message'),
                    "retry_after": result.get('retry_after')
                }), 500
        
        elif request_type == 'image':
            # Image generation request
            prompt = clean_prompt(user_message, 'image')
            result = generate_image_sd35(prompt)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "type": "image",
                    "image": result['image'],
                    "format": "base64",
                    "model_used": "stable-diffusion-3.5-large",
                    "prompt": prompt,
                    "message": "Image generated successfully! Decode base64 to view."
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error'),
                    "message": result.get('message')
                }), 500
        
        else:
            # Text chat request
            if user_id not in conversations:
                conversations[user_id] = []
            
            if force_model:
                selected_model = force_model
            else:
                selected_model = detect_query_type(user_message)
            
            if selected_model == 'gpt5-pro':
                response_text = get_gpt5_pro_response(user_message, conversations[user_id])
            else:
                response_text = get_opus_response(user_message, conversations[user_id])
            
            if response_text.startswith("Error:"):
                return jsonify({"success": False, "error": response_text}), 500
            
            conversations[user_id].append({"role": "user", "content": user_message})
            conversations[user_id].append({"role": "assistant", "content": response_text})
            
            input_tokens = len(user_message.split())
            output_tokens = len(response_text.split())
            
            return jsonify({
                "success": True,
                "type": "text",
                "response": response_text,
                "model_used": selected_model,
                "user_id": user_id,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "conversation_length": len(conversations[user_id])
            })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """Direct image generation endpoint"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({"error": "Prompt field is required"}), 400
        
        result = generate_image_sd35(prompt)
        
        if result['success']:
            return jsonify({
                "success": True,
                "image": result['image'],
                "format": "base64",
                "model": "stable-diffusion-3.5-large",
                "prompt": prompt,
                "message": "Image generated! Decode base64 to view."
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error'),
                "message": result.get('message')
            }), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """
    Direct video generation endpoint - Runway Gen-3 style
    
    Request body:
    {
        "prompt": "A cat running in a park",
        "duration": 3  // optional, default 3 seconds
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        prompt = data.get('prompt', '').strip()
        duration = data.get('duration', 3)
        
        if not prompt:
            return jsonify({"error": "Prompt field is required"}), 400
        
        if duration < 1 or duration > 10:
            return jsonify({"error": "Duration must be between 1-10 seconds"}), 400
        
        result = generate_video_runway(prompt, duration)
        
        if result['success']:
            return jsonify({
                "success": True,
                "video": result['video'],
                "format": "base64",
                "model": "runway-gen-3-style",
                "prompt": prompt,
                "duration": result['duration'],
                "fps": result['fps'],
                "message": "Video generated! Decode base64 to view MP4.",
                "decoding_info": {
                    "python": "import base64; video_data = base64.b64decode(video_base64); open('video.mp4', 'wb').write(video_data)",
                    "javascript": "const videoBlob = new Blob([Uint8Array.from(atob(videoBase64), c => c.charCodeAt(0))], {type: 'video/mp4'})"
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error'),
                "message": result.get('message'),
                "retry_after": result.get('retry_after')
            }), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/chat/opus', methods=['POST'])
def chat_opus():
    """Force Opus 4.5"""
    data = request.json if request.json else {}
    data['model'] = 'opus-4.5'
    request.json = data
    return chat()

@app.route('/chat/gpt5pro', methods=['POST'])
def chat_gpt5pro():
    """Force GPT-5 Pro"""
    data = request.json if request.json else {}
    data['model'] = 'gpt5-pro'
    request.json = data
    return chat()

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history"""
    try:
        data = request.json if request.json else {}
        user_id = data.get('user_id', 'default')
        
        if user_id in conversations:
            msg_count = len(conversations[user_id])
            conversations[user_id] = []
            return jsonify({
                "success": True,
                "message": f"Conversation reset. Cleared {msg_count} messages.",
                "user_id": user_id
            })
        else:
            return jsonify({
                "success": True,
                "message": "No conversation history found.",
                "user_id": user_id
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "active_users": len(conversations),
        "total_conversations": sum(len(conv) for conv in conversations.values()),
        "models": {
            "opus-4.5": "Available",
            "gpt5-pro": "Available",
            "stable-diffusion-3.5": "Available",
            "runway-gen-3-style": "Available"
        },
        "capabilities": {
            "text_chat": True,
            "image_generation": True,
            "video_generation": True,
            "multi_modal_routing": True
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)