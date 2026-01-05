import os
import json
import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
import requests
from threading import Thread
import queue

# Speech-to-Text & Text-to-Speech APIs (FREE)
GOOGLE_TTS_API = 'https://tts.google.com/api/v1/synthesis'  # Google Text-to-Speech
WHISPER_API = 'https://api-inference.huggingface.co/models/openai/whisper-base'  # Speech-to-Text
GROQ_API = 'https://api.groq.com/chat/completions'  # Fast LLM for real-time
REPLICATE_TTS = 'https://api.replicate.com/v1/predictions'  # Alternative TTS

# Live conversation queue for streaming
live_sessions = {}

class LiveConversationSession:
    """Manage a live conversation session"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_active = True
        self.conversation_history = []
        self.created_at = datetime.now()
        self.language = 'en'
    
    def add_audio(self, audio_data):
        """Add incoming audio to queue"""
        self.audio_queue.put(audio_data)
    
    def get_response(self):
        """Get response from queue"""
        try:
            return self.response_queue.get(timeout=30)
        except queue.Empty:
            return None
    
    def close(self):
        """Close session"""
        self.is_active = False

def transcribe_audio_whisper(audio_base64):
    """
    Convert audio to text using Whisper (FREE)
    Audio should be base64 encoded
    """
    try:
        audio_data = base64.b64decode(audio_base64)
        
        # Send to Whisper API
        headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY', 'hf_default')}" 
        }
        files = {'file': ('audio.wav', audio_data, 'audio/wav')}
        
        response = requests.post(
            WHISPER_API,
            headers=headers,
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')
            return {"success": True, "text": text}
        else:
            # Fallback: return placeholder
            return {"success": True, "text": "[Audio received - processing]", "raw": True}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def synthesize_speech_google(text, language='en'):
    """
    Convert text to speech using Google TTS (FREE)
    Returns base64 encoded audio
    """
    try:
        # Google Cloud TTS endpoint (free tier)
        params = {
            'text': text,
            'lang': 'en' if language != 'hi' else 'hi',
            'format': 'audio/mp3'
        }
        
        # Using free alternative: Pyttsx3 or gTTS
        # Direct approach using requests
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={'hi' if language == 'hi' else 'en'}&client=tw-ob"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return {"success": True, "audio": audio_base64, "format": "mp3"}
        else:
            return {"success": False, "error": "TTS API failed"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_live_response(text, conversation_history, language='en'):
    """
    Get real-time response for live conversation
    Using fast model for real-time interaction
    """
    try:
        # Build context
        system_prompt = f"""You are Claude 3.5 Sonnet in real-time conversation mode.
User language: {'Hindi' if language == 'hi' else 'English'}
Be conversational, brief, and natural.
Respond in same language as user.
Keep responses short (1-2 sentences) for audio chat."""
        
        # Build messages
        messages = []
        for msg in conversation_history[-5:]:  # Keep last 5 for context
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        messages.append({"role": "user", "content": text})
        
        # Try Groq API (fastest for live)
        groq_key = os.environ.get('GROQ_API_KEY', '')
        if groq_key:
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mixtral-8x7b-32768",  # Fast model
                "messages": [{"role": "system", "content": system_prompt}] + messages,
                "temperature": 0.7,
                "max_tokens": 256
            }
            
            response = requests.post(
                GROQ_API,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result['choices'][0]['message']['content'],
                    "model": "groq-mixtral"
                }
        
        # Fallback to regular API
        fallback_payload = {
            "messages": [
                {"role": "assistant", "content": "Hello! How can I help?"},
                {"role": "user", "content": system_prompt + "\n" + text}
            ]
        }
        
        fallback_response = requests.post(
            'https://chatbot-ji1z.onrender.com/chatbot-ji1z',
            json=fallback_payload,
            timeout=15
        )
        
        if fallback_response.status_code == 200:
            return {
                "success": True,
                "response": fallback_response.json()['choices'][0]['message']['content'],
                "model": "fallback"
            }
        
        return {
            "success": False,
            "error": "Unable to get response",
            "fallback": "Please try again"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": "Service temporarily busy"
        }

def create_live_conversation_app():
    """
    Create Flask app for live conversation
    """
    app = Flask(__name__)
    
    # Store sessions
    sessions = {}
    
    @app.route('/live/start', methods=['POST'])
    def start_live_session():
        """
        Start a live conversation session
        Returns session ID for managing conversation
        """
        try:
            data = request.json or {}
            session_id = data.get('session_id', f"live_{datetime.now().timestamp()}")
            language = data.get('language', 'en')
            
            # Create session
            session = LiveConversationSession(session_id)
            session.language = language
            sessions[session_id] = session
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "message": "Live conversation session started",
                "supports": {
                    "voice_input": True,
                    "text_input": True,
                    "audio_output": True,
                    "real_time": True
                },
                "languages": ["English", "Hindi", "Hinglish", "Urdu"],
                "timestamp": datetime.now().isoformat()
            })
        
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/live/audio', methods=['POST'])
    def process_audio():
        """
        Process audio input for live conversation
        Input: base64 encoded audio
        Output: base64 encoded audio response + text
        """
        try:
            data = request.json
            if not data or 'audio' not in data:
                return jsonify({"success": False, "error": "Audio data required"}), 400
            
            session_id = data.get('session_id')
            audio_base64 = data.get('audio')
            language = data.get('language', 'en')
            
            if session_id not in sessions:
                return jsonify({"success": False, "error": "Invalid session"}), 400
            
            session = sessions[session_id]
            
            # Step 1: Transcribe audio
            transcription = transcribe_audio_whisper(audio_base64)
            
            if not transcription['success']:
                return jsonify({
                    "success": False,
                    "error": "Failed to transcribe audio"
                }), 500
            
            user_text = transcription['text']
            
            # Step 2: Get response from AI
            ai_response = get_live_response(
                user_text,
                session.conversation_history,
                language
            )
            
            if not ai_response['success']:
                return jsonify(ai_response), 500
            
            response_text = ai_response['response']
            
            # Step 3: Convert response to speech
            tts_result = synthesize_speech_google(response_text, language)
            
            # Step 4: Update conversation history
            session.conversation_history.append({
                "role": "user",
                "content": user_text
            })
            session.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Return response
            response_data = {
                "success": True,
                "session_id": session_id,
                "user_input": user_text,
                "ai_response": response_text,
                "audio": tts_result.get('audio') if tts_result['success'] else None,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "conversation_length": len(session.conversation_history)
            }
            
            return jsonify(response_data)
        
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/live/text', methods=['POST'])
    def process_text():
        """
        Process text input for live conversation
        (alternative to audio input)
        """
        try:
            data = request.json
            if not data or 'message' not in data:
                return jsonify({"success": False, "error": "Message required"}), 400
            
            session_id = data.get('session_id')
            message = data.get('message')
            language = data.get('language', 'en')
            include_audio = data.get('include_audio', True)
            
            if session_id not in sessions:
                return jsonify({"success": False, "error": "Invalid session"}), 400
            
            session = sessions[session_id]
            
            # Get response
            ai_response = get_live_response(
                message,
                session.conversation_history,
                language
            )
            
            if not ai_response['success']:
                return jsonify(ai_response), 500
            
            response_text = ai_response['response']
            
            # Optionally convert to speech
            audio_data = None
            if include_audio:
                tts_result = synthesize_speech_google(response_text, language)
                audio_data = tts_result.get('audio') if tts_result['success'] else None
            
            # Update history
            session.conversation_history.append({
                "role": "user",
                "content": message
            })
            session.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "user_input": message,
                "ai_response": response_text,
                "audio": audio_data,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "conversation_length": len(session.conversation_history)
            })
        
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/live/end', methods=['POST'])
    def end_session():
        """
        End a live conversation session
        """
        try:
            data = request.json or {}
            session_id = data.get('session_id')
            
            if session_id not in sessions:
                return jsonify({"success": False, "error": "Session not found"}), 400
            
            session = sessions[session_id]
            conversation_summary = {
                "session_id": session_id,
                "duration": str(datetime.now() - session.created_at),
                "messages": len(session.conversation_history),
                "language": session.language,
                "conversation": session.conversation_history
            }
            
            # Close session
            session.close()
            del sessions[session_id]
            
            return jsonify({
                "success": True,
                "message": "Session ended",
                "summary": conversation_summary
            })
        
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/live/status', methods=['GET'])
    def session_status():
        """
        Get status of all active live sessions
        """
        try:
            status_data = {
                "active_sessions": len(sessions),
                "sessions": {}
            }
            
            for session_id, session in sessions.items():
                status_data["sessions"][session_id] = {
                    "active": session.is_active,
                    "duration": str(datetime.now() - session.created_at),
                    "messages": len(session.conversation_history),
                    "language": session.language
                }
            
            return jsonify(status_data)
        
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    return app

# Create app
live_app = create_live_conversation_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10001))
    live_app.run(host='0.0.0.0', port=port, debug=False)