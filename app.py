from flask import Flask, request, jsonify, send_file
import requests
import json
import os
import re
import base64
from io import BytesIO
import time
from datetime import datetime, timedelta
from PIL import Image
import PyPDF2
from docx import Document
from werkzeug.utils import secure_filename

# Optional imports - gracefully handle if not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("pandas not available - spreadsheet analysis disabled")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("google-generativeai not available - Gemini features disabled")

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("langdetect not available - using basic language detection")

try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    print("pytz not available - using basic timezone")

app = Flask(__name__)

# UNLIMITED CONFIGURATION - No Restrictions!
app.config['MAX_CONTENT_LENGTH'] = None  # Unlimited file size
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Enhanced conversation storage with metadata
conversations = {}

# UNLIMITED CONVERSATION SETTINGS
MAX_CONVERSATION_LENGTH = None  # Unlimited messages
CONTEXT_WINDOW = 20  # Increased context window

# API endpoints
OPUS_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
GPT5_PRO_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
IMAGE_GEN_API = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large'
VIDEO_GEN_API = 'https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b'

# Real-time Data APIs
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
EXCHANGE_API_KEY = os.environ.get('EXCHANGE_API_KEY', '')

# Configure Gemini for file analysis
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
gemini_model = None
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        gemini_model = None

# Allowed file extensions - UNLIMITED
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'ico'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'md'},
    'spreadsheet': {'xlsx', 'xls', 'csv', 'ods'},
    'code': {'py', 'js', 'java', 'cpp', 'c', 'html', 'css', 'json', 'xml'},
    'all': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'ico',
            'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'md',
            'xlsx', 'xls', 'csv', 'ods',
            'py', 'js', 'java', 'cpp', 'c', 'html', 'css', 'json', 'xml'}
}

# Multi-Language Support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'hi-en': 'Hinglish',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'ru': 'Russian',
    'pt': 'Portuguese',
    'it': 'Italian'
}

def detect_language(text):
    """Detect language of text with Hinglish support"""
    try:
        # Check for Hinglish patterns
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if hindi_chars > 0 and english_chars > 0:
            return 'hi-en'  # Hinglish
        elif hindi_chars > english_chars:
            return 'hi'  # Hindi
        
        # Use langdetect if available
        if LANGDETECT_AVAILABLE:
            lang = detect(text)
            return lang if lang in SUPPORTED_LANGUAGES else 'en'
        return 'en'
    except:
        return 'en'

def get_current_time_info():
    """Get current date, time, and day with IST timezone"""
    if PYTZ_AVAILABLE:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
    else:
        # Fallback to UTC+5:30
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    
    return {
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'day': now.strftime('%A'),
        'timestamp': now.isoformat(),
        'timezone': 'IST',
        'formatted': now.strftime('%d %B %Y, %I:%M %p IST')
    }

def fetch_real_time_news(query='latest', country='in', language='en'):
    """Fetch real-time news from NewsAPI"""
    try:
        if not NEWSAPI_KEY:
            return None
        
        url = f'https://newsapi.org/v2/top-headlines?country={country}&q={query}&apiKey={NEWSAPI_KEY}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])[:5]
            
            news_summary = []
            for article in articles:
                news_summary.append({
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'source': article.get('source', {}).get('name'),
                    'url': article.get('url'),
                    'published': article.get('publishedAt')
                })
            
            return news_summary
        return None
    except:
        return None

def fetch_weather_data(city='Lucknow'):
    """Fetch real-time weather data"""
    try:
        if not WEATHER_API_KEY:
            return None
        
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('name'),
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed']
            }
        return None
    except:
        return None

def fetch_crypto_prices():
    """Fetch real-time cryptocurrency prices"""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,dogecoin&vs_currencies=usd,inr'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def search_web(query, num_results=5):
    """Search the web for real-time information"""
    try:
        url = f'https://api.duckduckgo.com/?q={query}&format=json&no_html=1'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            results = {
                'abstract': data.get('AbstractText', ''),
                'source': data.get('AbstractSource', ''),
                'url': data.get('AbstractURL', ''),
                'related': []
            }
            
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if 'Text' in topic:
                    results['related'].append({
                        'text': topic.get('Text'),
                        'url': topic.get('FirstURL', '')
                    })
            
            return results
        return None
    except:
        return None

def check_for_real_time_query(message):
    """Check if message requires real-time data"""
    message_lower = message.lower()
    
    time_keywords = ['time', 'date', 'day', 'today', 'now', 'current', 'समय', 'तारीख', 'आज']
    news_keywords = ['news', 'latest', 'breaking', 'headlines', 'समाचार', 'खबर']
    weather_keywords = ['weather', 'temperature', 'climate', 'मौसम', 'तापमान']
    crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'cryptocurrency', 'btc', 'eth']
    search_keywords = ['search', 'find', 'lookup', 'what is', 'who is', 'खोजो', 'ढूंढो']
    
    if any(keyword in message_lower for keyword in time_keywords):
        return 'time'
    elif any(keyword in message_lower for keyword in news_keywords):
        return 'news'
    elif any(keyword in message_lower for keyword in weather_keywords):
        return 'weather'
    elif any(keyword in message_lower for keyword in crypto_keywords):
        return 'crypto'
    elif any(keyword in message_lower for keyword in search_keywords):
        return 'search'
    
    return None

def get_real_time_data(query_type, message):
    """Fetch real-time data based on query type"""
    data = {}
    
    if query_type == 'time':
        data['time_info'] = get_current_time_info()
    
    elif query_type == 'news':
        topic = re.sub(r'(news|latest|breaking|headlines|about|समाचार|खबर)', '', message.lower()).strip()
        data['news'] = fetch_real_time_news(topic if topic else 'latest')
    
    elif query_type == 'weather':
        city_match = re.search(r'in ([a-zA-Z\s]+)', message.lower())
        city = city_match.group(1) if city_match else 'Lucknow'
        data['weather'] = fetch_weather_data(city)
    
    elif query_type == 'crypto':
        data['crypto'] = fetch_crypto_prices()
    
    elif query_type == 'search':
        search_query = re.sub(r'(search|find|lookup|what is|who is|खोजो|ढूंढो)', '', message.lower()).strip()
        data['search_results'] = search_web(search_query)
    
    return data

def init_conversation(user_id):
    """Initialize a new conversation for a user"""
    if user_id not in conversations:
        conversations[user_id] = {
            "messages": [],
            "context": {
                "topics": [],
                "entities": [],
                "last_intent": None,
                "language": 'en',
                "location": None
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "message_count": 0,
                "user_preferences": {},
                "total_tokens": 0
            }
        }

def update_conversation_context(user_id, message, response, language='en'):
    """Update conversation context with new information"""
    if user_id not in conversations:
        init_conversation(user_id)
    
    conv = conversations[user_id]
    
    conv["messages"].append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat(),
        "language": language
    })
    conv["messages"].append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat(),
        "language": language
    })
    
    conv["context"]["language"] = language
    
    topic_keywords = {
        'coding': ['code', 'programming', 'function', 'algorithm', 'debug', 'कोड', 'प्रोग्रामिंग'],
        'data_analysis': ['data', 'analysis', 'chart', 'graph', 'statistics', 'डेटा', 'विश्लेषण'],
        'creative': ['image', 'video', 'design', 'creative', 'art', 'तस्वीर', 'वीडियो'],
        'document': ['pdf', 'document', 'text', 'file', 'extract', 'दस्तावेज़'],
        'education': ['learn', 'study', 'teach', 'course', 'सीखना', 'पढ़ाई'],
        'news': ['news', 'current', 'latest', 'समाचार', 'खबर'],
        'weather': ['weather', 'temperature', 'climate', 'मौसम']
    }
    
    message_lower = message.lower()
    for topic, keywords in topic_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            if topic not in conv["context"]["topics"]:
                conv["context"]["topics"].append(topic)
    
    conv["metadata"]["last_active"] = datetime.now().isoformat()
    conv["metadata"]["message_count"] = len(conv["messages"])

def get_conversation_context(user_id):
    """Get recent conversation context for continuity"""
    if user_id not in conversations:
        return []
    
    conv = conversations[user_id]
    recent_messages = conv["messages"][-CONTEXT_WINDOW:] if CONTEXT_WINDOW else conv["messages"]
    
    context_messages = []
    for msg in recent_messages:
        context_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return context_messages

def get_conversation_summary(user_id):
    """Generate a summary of the conversation"""
    if user_id not in conversations:
        return "No conversation history."
    
    conv = conversations[user_id]
    topics = conv["context"]["topics"]
    msg_count = conv["metadata"]["message_count"]
    language = conv["context"]["language"]
    
    if msg_count == 0:
        return "No messages yet."
    
    summary = f"Conversation has {msg_count} messages in {SUPPORTED_LANGUAGES.get(language, 'English')}."
    if topics:
        summary += f" Topics discussed: {', '.join(topics)}."
    
    return summary

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS['all']

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS['image']:
        return 'image'
    elif ext in ALLOWED_EXTENSIONS['document']:
        return 'document'
    elif ext in ALLOWED_EXTENSIONS['spreadsheet']:
        return 'spreadsheet'
    elif ext in ALLOWED_EXTENSIONS['code']:
        return 'code'
    return 'unknown'

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from Word document"""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def analyze_spreadsheet(file_path, file_ext):
    """Analyze Excel or CSV file"""
    if not PANDAS_AVAILABLE:
        return {"error": "Spreadsheet analysis not available. Please configure pandas."}
    
    try:
        if file_ext == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        analysis = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "summary": df.describe().to_dict() if len(df) > 0 else {},
            "preview": df.head(10).to_dict('records'),
            "missing_values": df.isnull().sum().to_dict()
        }
        return analysis
    except Exception as e:
        return {"error": f"Error analyzing spreadsheet: {str(e)}"}

def analyze_image_with_gemini(image_path, question="Analyze this image in detail"):
    """Analyze image using Google Gemini Flash"""
    try:
        if not gemini_model:
            return "Image analysis requires Gemini API configuration."
        
        img = Image.open(image_path)
        response = gemini_model.generate_content([question, img])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def analyze_document_with_ai(text, question="Analyze this document"):
    """Analyze document text using AI"""
    try:
        if gemini_model:
            prompt = f"{question}\n\nDocument Content:\n{text}"
            response = gemini_model.generate_content(prompt)
            return response.text
        else:
            return get_gpt5_pro_response(f"{question}\n\nDocument: {text}")
    except Exception as e:
        return f"Error analyzing document: {str(e)}"

def detect_request_type(message):
    """Detect if request is for video, image generation or text chat"""
    message_lower = message.lower()
    
    video_keywords = [
        'generate video', 'create video', 'make video', 'video of',
        'animate', 'animation', 'moving', 'motion', 'video clip',
        'वीडियो बनाओ', 'एनीमेशन बनाओ'
    ]
    
    image_keywords = [
        'generate image', 'create image', 'make image', 'draw', 'paint',
        'generate picture', 'create picture', 'visualize', 'illustrate',
        'image of', 'picture of', 'photo of', 'render', 'design image',
        'तस्वीर बनाओ', 'फोटो बनाओ', 'इमेज बनाओ'
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
        'code', 'debug', 'algorithm', 'implement', 'function',
        'programming', 'develop', 'build', 'create app',
        'research', 'analyze', 'analysis', 'detailed', 'comprehensive'
    ]
    
    gpt5_score = sum(1 for keyword in gpt5_pro_keywords if keyword in question_lower)
    word_count = len(question.split())
    
    if word_count > 50 or gpt5_score > 2:
        return 'gpt5-pro'
    
    return 'opus-4.5'

def clean_prompt(message, content_type='image'):
    """Extract clean prompt for image/video generation"""
    message_lower = message.lower()
    
    if content_type == 'video':
        triggers = ['generate video of', 'create video of', 'make video of', 'video of', 'animate']
    else:
        triggers = ['generate image of', 'create image of', 'make image of', 'image of', 'picture of', 'photo of', 'draw']
    
    prompt = message
    for trigger in triggers:
        if trigger in message_lower:
            idx = message_lower.find(trigger)
            prompt = message[idx + len(trigger):].strip()
            break
    
    return prompt

def generate_video_runway(prompt, duration=3):
    """Generate video"""
    try:
        headers = {"Content-Type": "application/json"}
        enhanced_prompt = f"{prompt}, high quality, cinematic, 4k"
        
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {"num_frames": duration * 8}
        }
        
        response = requests.post(VIDEO_GEN_API, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            video_bytes = response.content
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
            return {"success": True, "video": video_base64}
        else:
            return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_image_sd35(prompt):
    """Generate image"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": prompt}
        
        response = requests.post(IMAGE_GEN_API, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            image_bytes = response.content
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            return {"success": True, "image": img_base64}
        else:
            return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_opus_response(question, conversation_history=[], language='en', real_time_data=None):
    """Opus chat with professional tone"""
    messages = []
    
    time_info = get_current_time_info()
    system_context = f"You are a premium AI assistant. Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language, 'English')}. Provide professional, helpful responses."
    
    if real_time_data:
        system_context += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
    
    messages.append({'role': 'system', 'content': system_context})
    
    for msg in conversation_history:
        messages.append(msg)
    messages.append({'role': 'user', 'content': question})
    
    payload = {'messages': messages}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(OPUS_API, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Service temporarily unavailable (Status: {response.status_code})"
    except Exception as e:
        return f"Service error: {str(e)}"

def get_gpt5_pro_response(question, conversation_history=[], language='en', real_time_data=None):
    """GPT-5 Pro with professional tone"""
    messages = []
    
    time_info = get_current_time_info()
    system_prompt = (
        f"You are an elite AI assistant providing exceptional service. "
        f"Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language, 'English')}. "
        f"Deliver comprehensive, well-structured, professional responses."
    )
    
    if real_time_data:
        system_prompt += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
    
    messages.append({'role': 'assistant', 'content': system_prompt})
    
    for msg in conversation_history:
        messages.append(msg)
    
    messages.append({'role': 'user', 'content': question})
    
    payload = {'messages': messages}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(GPT5_PRO_API, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Premium service temporarily unavailable (Status: {response.status_code})"
    except Exception as e:
        return f"Service error: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    """API status"""
    return jsonify({
        "status": "operational",
        "message": "🚀 Premium Multi-Modal AI Platform - Professional Edition",
        "version": "6.0.0",
        "features": {
            "multi_language": True,
            "real_time_data": True,
            "unlimited_conversations": True,
            "image_generation": True,
            "video_generation": True,
            "file_analysis": True
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
                    "prompt": prompt
                })
            else:
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
                    "prompt": prompt
                })
            else:
                return jsonify({"success": False, "error": result.get('error')}), 500
        
        else:
            conversation_history = get_conversation_context(user_id)
            selected_model = detect_query_type(user_message)
            
            if selected_model == 'gpt5-pro':
                response_text = get_gpt5_pro_response(user_message, conversation_history, detected_language, real_time_data)
            else:
                response_text = get_opus_response(user_message, conversation_history, detected_language, real_time_data)
            
            update_conversation_context(user_id, user_message, response_text, detected_language)
            
            return jsonify({
                "success": True,
                "type": "text",
                "response": response_text,
                "model_used": selected_model,
                "language": SUPPORTED_LANGUAGES.get(detected_language),
                "conversation_length": conversations[user_id]["metadata"]["message_count"]
            })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "optimal",
        "message": "All systems operational",
        "active_users": len(conversations),
        "features": {
            "pandas": PANDAS_AVAILABLE,
            "gemini": GEMINI_AVAILABLE and gemini_model is not None,
            "langdetect": LANGDETECT_AVAILABLE,
            "pytz": PYTZ_AVAILABLE
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)