from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Conversation storage
conversations = {}

def get_chatbot_response(question, conversation_history=[]):
    """Function to get response from free chatbot API"""
    
    # Build messages from conversation history
    messages = []
    
    # Add conversation history
    for msg in conversation_history:
        messages.append(msg)
    
    # Add current question
    messages.append({
        'role': 'user',
        'content': question
    })
    
    payload = {
        'messages': messages
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    url = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            api_response = response.json()
            return api_response['choices'][0]['message']['content']
        else:
            return f"Error: Status code {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "Error: Request timeout. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid response format"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    """Home endpoint - API status"""
    return jsonify({
        "status": "active",
        "message": "Free AI Chatbot API is running",
        "model": "opus-4.5-equivalent",
        "version": "1.0",
        "endpoints": {
            "/": "GET - API status",
            "/chat": "POST - Send message to chatbot",
            "/reset": "POST - Reset conversation history"
        },
        "features": [
            "Conversation history tracking",
            "Multiple user support",
            "Free to use - No API key needed",
            "Claude Opus 4.5 level responses"
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint - Send message and get response"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Invalid request. JSON body required."}), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({"error": "Message field is required and cannot be empty."}), 400
        
        # Get or create conversation history for user
        if user_id not in conversations:
            conversations[user_id] = []
        
        # Get response from chatbot
        response_text = get_chatbot_response(user_message, conversations[user_id])
        
        # Check if response is error
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
        
        # Calculate token estimate (rough)
        input_tokens = len(user_message.split())
        output_tokens = len(response_text.split())
        
        return jsonify({
            "success": True,
            "response": response_text,
            "model": "opus-4.5-equivalent",
            "user_id": user_id,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            "conversation_length": len(conversations[user_id])
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history for a user"""
    try:
        data = request.json if request.json else {}
        user_id = data.get('user_id', 'default')
        
        if user_id in conversations:
            msg_count = len(conversations[user_id])
            conversations[user_id] = []
            return jsonify({
                "success": True,
                "message": f"Conversation reset successfully. Cleared {msg_count} messages.",
                "user_id": user_id
            })
        else:
            return jsonify({
                "success": True,
                "message": "No conversation history found for this user.",
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
        "total_conversations": sum(len(conv) for conv in conversations.values())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)