from flask import Flask, request, jsonify
import requests
import json
import os
import re

app = Flask(__name__)

# Conversation storage
conversations = {}

# API endpoints
OPUS_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
GPT5_PRO_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'  # Same backend, different prompting

def detect_query_type(question):
    """Intelligent query type detection - Decides which API to use"""
    question_lower = question.lower()
    
    # GPT-5 Pro equivalent triggers (Complex, Critical, High-Precision)
    gpt5_pro_keywords = [
        # Coding & Development
        'code', 'debug', 'algorithm', 'implement', 'function', 'class', 'api',
        'programming', 'software', 'develop', 'build', 'create app', 'script',
        'refactor', 'optimize', 'bug', 'error', 'python', 'javascript', 'react',
        
        # Research & Analysis
        'research', 'analyze', 'analysis', 'study', 'investigate', 'examine',
        'compare', 'evaluate', 'review', 'assess', 'scientific', 'academic',
        
        # Complex Reasoning
        'solve', 'calculate', 'compute', 'mathematical', 'proof', 'logic',
        'reasoning', 'explain complex', 'detailed explanation', 'step by step',
        
        # Professional Tasks
        'legal', 'medical', 'financial', 'business plan', 'strategy',
        'technical document', 'architecture', 'design system',
        
        # Long-form Content
        'essay', 'article', 'report', 'documentation', 'proposal',
        'comprehensive', 'detailed', 'in-depth'
    ]
    
    # Opus 4.5 equivalent triggers (General, Fast, Conversational)
    opus_keywords = [
        'hello', 'hi', 'hey', 'what is', 'tell me about', 'explain',
        'simple', 'quick', 'summary', 'summarize', 'brief',
        'translate', 'meaning', 'definition', 'who is', 'where is',
        'general', 'basic', 'simple question'
    ]
    
    # Check for GPT-5 Pro triggers
    gpt5_score = sum(1 for keyword in gpt5_pro_keywords if keyword in question_lower)
    opus_score = sum(1 for keyword in opus_keywords if keyword in question_lower)
    
    # Length-based detection
    word_count = len(question.split())
    if word_count > 50:  # Long queries need GPT-5 Pro
        gpt5_score += 2
    
    # Code detection
    if '```' in question or 'def ' in question or 'function' in question:
        gpt5_score += 3
    
    # Question complexity
    if '?' in question:
        question_marks = question.count('?')
        if question_marks > 2:  # Multiple questions
            gpt5_score += 1
    
    # Decision
    if gpt5_score > opus_score:
        return 'gpt5-pro'
    else:
        return 'opus-4.5'

def get_opus_response(question, conversation_history=[]):
    """Opus 4.5 equivalent - Fast, general queries"""
    messages = []
    
    for msg in conversation_history:
        messages.append(msg)
    
    messages.append({
        'role': 'user',
        'content': question
    })
    
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
    """GPT-5 Pro equivalent - Complex, detailed queries"""
    messages = []
    
    # Add system prompt for enhanced reasoning
    system_prompt = (
        "You are an advanced AI assistant with GPT-5 Pro level capabilities. "
        "Provide detailed, accurate, and well-reasoned responses. "
        "For coding tasks, write production-ready code with best practices. "
        "For analysis, provide comprehensive insights with examples. "
        "Think step-by-step and show your reasoning when appropriate."
    )
    
    messages.append({
        'role': 'assistant',
        'content': system_prompt
    })
    
    for msg in conversation_history:
        messages.append(msg)
    
    # Enhanced question with reasoning trigger
    enhanced_question = (
        f"Please provide a detailed, comprehensive response with step-by-step reasoning: {question}"
    )
    
    messages.append({
        'role': 'user',
        'content': enhanced_question
    })
    
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
        "message": "Intelligent Dual AI API Router",
        "models": {
            "opus-4.5": "Fast, general queries",
            "gpt5-pro": "Complex, detailed tasks"
        },
        "version": "2.0",
        "endpoints": {
            "/": "GET - API status",
            "/chat": "POST - Intelligent chat routing",
            "/chat/opus": "POST - Force Opus 4.5",
            "/chat/gpt5pro": "POST - Force GPT-5 Pro",
            "/reset": "POST - Reset conversation",
            "/health": "GET - Health check"
        },
        "features": [
            "Intelligent query routing",
            "Dual model support",
            "Conversation history",
            "Free to use",
            "Auto model selection"
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Intelligent chat endpoint - Auto-selects best model"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Invalid request. JSON body required."}), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        force_model = data.get('model', None)  # Optional: 'opus' or 'gpt5pro'
        
        if not user_message:
            return jsonify({"error": "Message field is required."}), 400
        
        # Get or create conversation history
        if user_id not in conversations:
            conversations[user_id] = []
        
        # Intelligent model selection
        if force_model:
            selected_model = force_model
        else:
            selected_model = detect_query_type(user_message)
        
        # Get response from selected model
        if selected_model == 'gpt5-pro':
            response_text = get_gpt5_pro_response(user_message, conversations[user_id])
        else:
            response_text = get_opus_response(user_message, conversations[user_id])
        
        # Check for errors
        if response_text.startswith("Error:"):
            return jsonify({
                "success": False,
                "error": response_text
            }), 500
        
        # Add to conversation history
        conversations[user_id].append({
            "role": "user",
            "content": user_message
        })
        conversations[user_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Token estimation
        input_tokens = len(user_message.split())
        output_tokens = len(response_text.split())
        
        return jsonify({
            "success": True,
            "response": response_text,
            "model_used": selected_model,
            "user_id": user_id,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            "conversation_length": len(conversations[user_id]),
            "routing_info": {
                "auto_selected": force_model is None,
                "reason": "Intelligent query analysis" if force_model is None else "User forced"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/chat/opus', methods=['POST'])
def chat_opus():
    """Force Opus 4.5 equivalent"""
    data = request.json if request.json else {}
    data['model'] = 'opus-4.5'
    request.json = data
    return chat()

@app.route('/chat/gpt5pro', methods=['POST'])
def chat_gpt5pro():
    """Force GPT-5 Pro equivalent"""
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
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "active_users": len(conversations),
        "total_conversations": sum(len(conv) for conv in conversations.values()),
        "models": {
            "opus-4.5": "Available",
            "gpt5-pro": "Available"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)