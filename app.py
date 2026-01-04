from flask import Flask, request, jsonify
import anthropic
import os

app = Flask(__name__)

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Conversation storage (in production, use database)
conversations = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "active",
        "message": "Claude Opus 4.5 API is running",
        "model": "claude-opus-4-5",
        "endpoints": {
            "/chat": "POST - Send message to chatbot",
            "/reset": "POST - Reset conversation"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get or create conversation history
        if user_id not in conversations:
            conversations[user_id] = []
        
        # Add user message to history
        conversations[user_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Create message with Claude Opus 4.5
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            messages=conversations[user_id]
        )
        
        # Get assistant response
        assistant_response = message.content[0].text
        
        # Add assistant response to history
        conversations[user_id].append({
            "role": "assistant",
            "content": assistant_response
        })
        
        return jsonify({
            "success": True,
            "response": assistant_response,
            "model": message.model,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        })
        
    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key"}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit exceeded"}), 429
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        
        if user_id in conversations:
            conversations[user_id] = []
        
        return jsonify({
            "success": True,
            "message": "Conversation reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)