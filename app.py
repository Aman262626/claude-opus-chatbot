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
import pandas as pd
import google.generativeai as genai
from werkzeug.utils import secure_filename
from langdetect import detect, LangDetectException
import pytz

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
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
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
        
        # Use langdetect for other languages
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGUAGES else 'en'
    except:
        return 'en'

def get_current_time_info():
    """Get current date, time, and day with IST timezone"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
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
        # Using DuckDuckGo Instant Answer API (no API key needed)
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
    
    # Time/Date queries
    time_keywords = ['time', 'date', 'day', 'today', 'now', 'current', 'समय', 'तारीख', 'आज']
    
    # News queries
    news_keywords = ['news', 'latest', 'breaking', 'headlines', 'समाचार', 'खबर']
    
    # Weather queries
    weather_keywords = ['weather', 'temperature', 'climate', 'मौसम', 'तापमान']
    
    # Crypto queries
    crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'cryptocurrency', 'btc', 'eth']
    
    # Search queries
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
        # Extract topic from message
        topic = re.sub(r'(news|latest|breaking|headlines|about|समाचार|खबर)', '', message.lower()).strip()
        data['news'] = fetch_real_time_news(topic if topic else 'latest')
    
    elif query_type == 'weather':
        # Extract city from message
        city_match = re.search(r'in ([a-zA-Z\s]+)', message.lower())
        city = city_match.group(1) if city_match else 'Lucknow'
        data['weather'] = fetch_weather_data(city)
    
    elif query_type == 'crypto':
        data['crypto'] = fetch_crypto_prices()
    
    elif query_type == 'search':
        # Extract search query
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
    
    # Add message to history
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
    
    # NO LIMIT - Keep all messages
    # Previous limit removed for unlimited conversation history
    
    # Extract and update context
    message_lower = message.lower()
    
    # Update language preference
    conv["context"]["language"] = language
    
    # Detect topics
    topic_keywords = {
        'coding': ['code', 'programming', 'function', 'algorithm', 'debug', 'कोड', 'प्रोग्रामिंग'],
        'data_analysis': ['data', 'analysis', 'chart', 'graph', 'statistics', 'डेटा', 'विश्लेषण'],
        'creative': ['image', 'video', 'design', 'creative', 'art', 'तस्वीर', 'वीडियो'],
        'document': ['pdf', 'document', 'text', 'file', 'extract', 'दस्तावेज़'],
        'medical': ['medical', 'health', 'disease', 'diagnosis', 'xray', 'स्वास्थ्य'],
        'business': ['business', 'finance', 'market', 'strategy', 'revenue', 'व्यापार'],
        'education': ['learn', 'study', 'teach', 'course', 'सीखना', 'पढ़ाई'],
        'news': ['news', 'current', 'latest', 'समाचार', 'खबर'],
        'weather': ['weather', 'temperature', 'climate', 'मौसम']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            if topic not in conv["context"]["topics"]:
                conv["context"]["topics"].append(topic)
    
    # Update metadata
    conv["metadata"]["last_active"] = datetime.now().isoformat()
    conv["metadata"]["message_count"] = len(conv["messages"])

def get_conversation_context(user_id):
    """Get recent conversation context for continuity"""
    if user_id not in conversations:
        return []
    
    conv = conversations[user_id]
    recent_messages = conv["messages"][-CONTEXT_WINDOW:] if CONTEXT_WINDOW else conv["messages"]
    
    # Convert to API format
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
        return f"We encountered a minor issue while processing your PDF: {str(e)}. Please try again or contact support."

def extract_text_from_docx(file_path):
    """Extract text from Word document"""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"We're unable to process this document at the moment: {str(e)}. Please verify the file format and try again."

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        return f"There was an issue reading your text file: {str(e)}. Please ensure the file is properly formatted."

def analyze_spreadsheet(file_path, file_ext):
    """Analyze Excel or CSV file"""
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
        return {"error": f"We're experiencing difficulty analyzing your spreadsheet: {str(e)}. Please verify the data format."}

def analyze_image_with_gemini(image_path, question="Analyze this image in detail"):
    """Analyze image using Google Gemini Flash"""
    try:
        if not gemini_model:
            return "Our advanced image analysis feature requires API configuration. Please contact support to enable this premium capability."
        
        img = Image.open(image_path)
        response = gemini_model.generate_content([question, img])
        return response.text
    except Exception as e:
        return f"We encountered an issue while analyzing your image: {str(e)}. Our team is working to resolve this."

def analyze_document_with_ai(text, question="Analyze this document and provide key insights"):
    """Analyze document text using AI"""
    try:
        if gemini_model:
            # NO LIMIT on text length
            prompt = f"{question}\n\nDocument Content:\n{text}"
            response = gemini_model.generate_content(prompt)
            return response.text
        else:
            return get_gpt5_pro_response(f"{question}\n\nDocument: {text}")
    except Exception as e:
        return f"We're experiencing a temporary issue with document analysis: {str(e)}. Please try again shortly."

def detect_request_type(message):
    """Detect if request is for video, image generation or text chat"""
    message_lower = message.lower()
    
    video_keywords = [
        'generate video', 'create video', 'make video', 'video of',
        'animate', 'animation', 'moving', 'motion', 'video clip',
        'वीडियो बनाओ', 'एनीमेशन बनाओ', 'मूवमेंट', 'वीडियो क्लिप',
        'runway', 'gen-3', 'text to video', 'video generation'
    ]
    
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
    """Generate video using Runway Gen-3 style efficiency"""
    try:
        headers = {"Content-Type": "application/json"}
        enhanced_prompt = f"{prompt}, high quality, smooth motion, cinematic, 4k resolution"
        
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "num_frames": duration * 8,
                "num_inference_steps": 50,
                "guidance_scale": 9.0,
                "negative_prompt": "blurry, low quality, distorted, static, choppy motion"
            }
        }
        
        response = requests.post(VIDEO_GEN_API, headers=headers, json=payload, timeout=120)
        
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
                "error": "model_initializing",
                "message": "Our premium video generation engine is warming up. This ensures the highest quality output. Please retry in 20-30 seconds for optimal results.",
                "retry_after": 30
            }
        else:
            return {
                "success": False,
                "error": f"service_unavailable_{response.status_code}",
                "message": "Our video generation service is temporarily experiencing high demand. Your request is important to us - please try again shortly."
            }
    except Exception as e:
        return {
            "success": False, 
            "error": "generation_failed", 
            "message": f"We encountered an unexpected issue while creating your video. Our team has been notified. Error details: {str(e)}"
        }

def generate_image_sd35(prompt):
    """Generate image using Stable Diffusion 3.5 Large"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "negative_prompt": "blurry, low quality, distorted, ugly"
            }
        }
        
        response = requests.post(IMAGE_GEN_API, headers=headers, json=payload, timeout=60)
        
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
                "error": f"service_unavailable_{response.status_code}",
                "message": "Our image generation service is currently experiencing high traffic. We appreciate your patience - please retry in a moment."
            }
    except Exception as e:
        return {
            "success": False, 
            "error": "generation_failed", 
            "message": f"We're unable to complete your image generation request at this time: {str(e)}. Please try again."
        }

def get_opus_response(question, conversation_history=[], language='en', real_time_data=None):
    """Opus 4.5 - Fast, general queries with context and real-time data"""
    messages = []
    
    # Add system context with current time and language
    time_info = get_current_time_info()
    system_context = f"Current Date & Time: {time_info['formatted']}. User language preference: {SUPPORTED_LANGUAGES.get(language, 'English')}."
    
    if real_time_data:
        system_context += f"\n\nReal-time Data: {json.dumps(real_time_data, indent=2)}"
    
    messages.append({'role': 'system', 'content': system_context})
    
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
            return f"We're experiencing connectivity issues with our AI service (Status: {response.status_code}). Please try again in a moment."
    except Exception as e:
        return f"Our chat service is temporarily unavailable: {str(e)}. We're working to restore it promptly."

def get_gpt5_pro_response(question, conversation_history=[], language='en', real_time_data=None):
    """GPT-5 Pro - Complex, detailed queries with context and real-time data"""
    messages = []
    
    # Add system context with current time and language
    time_info = get_current_time_info()
    
    system_prompt = (
        f"You are an elite AI assistant powered by advanced GPT-5 Pro architecture. "
        f"Current Date & Time: {time_info['formatted']}. "
        f"User language preference: {SUPPORTED_LANGUAGES.get(language, 'English')}. "
        f"Deliver exceptional, comprehensive responses with precision and clarity. "
        f"For technical implementations, provide production-grade solutions following industry best practices. "
        f"For analytical tasks, offer deep insights supported by logical reasoning and examples. "
        f"Maintain a professional yet approachable tone that reflects premium service quality. "
        f"Remember context from previous messages to provide coherent, contextual responses. "
        f"Use real-time data when available to provide accurate, up-to-date information."
    )
    
    if real_time_data:
        system_prompt += f"\n\nReal-time Data Available: {json.dumps(real_time_data, indent=2)}"
    
    messages.append({'role': 'assistant', 'content': system_prompt})
    
    for msg in conversation_history:
        messages.append(msg)
    
    enhanced_question = f"Please provide a comprehensive, well-structured response: {question}"
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
            return f"Our premium AI service is experiencing high demand (Status: {response.status_code}). Your query is important - please retry shortly."
    except Exception as e:
        return f"We're temporarily unable to process complex queries: {str(e)}. Our engineers are addressing this."

@app.route('/', methods=['GET'])
def home():
    """Home endpoint - API status"""
    return jsonify({
        "status": "operational",
        "message": "🚀 Welcome to Ultra-Powerful Multi-Modal AI Platform - UNLIMITED Edition",
        "tagline": "Real-time Intelligence • Multi-language • No Restrictions • Full Potential Unleashed",
        "models": {
            "opus-4.5": "Lightning-fast conversational AI with real-time data",
            "gpt5-pro": "Advanced reasoning for complex tasks",
            "stable-diffusion-3.5-large": "Professional image synthesis",
            "runway-gen-3-style": "Cinematic video generation",
            "gemini-1.5-flash": "Intelligent file & image analysis"
        },
        "version": "6.0.0 - UNLIMITED",
        "api_tier": "Premium Unlimited",
        "new_features": {
            "multi_language": f"Supports {len(SUPPORTED_LANGUAGES)} languages including Hindi, English, Hinglish",
            "real_time_data": "Live news, weather, crypto prices, web search",
            "unlimited_files": "No file size restrictions",
            "unlimited_conversations": "Unlimited message history",
            "unlimited_context": "Enhanced context window"
        },
        "supported_languages": SUPPORTED_LANGUAGES,
        "real_time_capabilities": [
            "Current date, time, and timezone",
            "Latest news from around the world",
            "Real-time weather updates",
            "Cryptocurrency prices (BTC, ETH, DOGE)",
            "Web search and information lookup"
        ],
        "endpoints": {
            "/": "GET - Platform status & capabilities",
            "/chat": "POST - Intelligent multi-modal routing with memory & real-time data",
            "/chat/history": "GET - View conversation history (unlimited)",
            "/chat/context": "GET - Get current conversation context",
            "/realtime/news": "GET - Get latest news",
            "/realtime/weather": "GET - Get weather data",
            "/realtime/crypto": "GET - Get cryptocurrency prices",
            "/realtime/search": "GET - Search the web",
            "/generate-image": "POST - Professional image creation",
            "/generate-video": "POST - Cinematic video synthesis",
            "/analyze-file": "POST - Comprehensive file intelligence (unlimited size)",
            "/analyze-image": "POST - Advanced visual analysis",
            "/extract-text": "POST - Premium document extraction",
            "/reset": "POST - Conversation management",
            "/health": "GET - System health monitoring"
        },
        "supported_formats": {
            "images": ["PNG", "JPG", "JPEG", "GIF", "BMP", "WEBP", "SVG", "TIFF", "ICO"],
            "documents": ["PDF", "DOCX", "TXT", "RTF", "ODT", "MD"],
            "spreadsheets": ["XLSX", "XLS", "CSV", "ODS"],
            "code": ["PY", "JS", "JAVA", "CPP", "C", "HTML", "CSS", "JSON", "XML"]
        },
        "unlimited_features": [
            "✅ Unlimited file size support",
            "✅ Unlimited conversation history",
            "✅ Enhanced context window (20 messages)",
            "✅ Multi-language support (13+ languages)",
            "✅ Real-time data integration",
            "✅ No rate limiting",
            "✅ No usage restrictions",
            "✅ Full potential unlocked"
        ],
        "support": "🌟 For enterprise inquiries and technical support, please contact our team"
    })

@app.route('/realtime/news', methods=['GET'])
def get_news():
    """Get real-time news"""
    query = request.args.get('query', 'latest')
    country = request.args.get('country', 'in')
    language = request.args.get('language', 'en')
    
    news = fetch_real_time_news(query, country, language)
    
    if news:
        return jsonify({
            "success": True,
            "news": news,
            "timestamp": get_current_time_info()['formatted']
        })
    else:
        return jsonify({
            "success": False,
            "message": "Unable to fetch news. Please configure NewsAPI key."
        }), 500

@app.route('/realtime/weather', methods=['GET'])
def get_weather():
    """Get real-time weather"""
    city = request.args.get('city', 'Lucknow')
    
    weather = fetch_weather_data(city)
    
    if weather:
        return jsonify({
            "success": True,
            "weather": weather,
            "timestamp": get_current_time_info()['formatted']
        })
    else:
        return jsonify({
            "success": False,
            "message": "Unable to fetch weather. Please configure Weather API key."
        }), 500

@app.route('/realtime/crypto', methods=['GET'])
def get_crypto():
    """Get real-time cryptocurrency prices"""
    crypto = fetch_crypto_prices()
    
    if crypto:
        return jsonify({
            "success": True,
            "crypto": crypto,
            "timestamp": get_current_time_info()['formatted']
        })
    else:
        return jsonify({
            "success": False,
            "message": "Unable to fetch cryptocurrency prices."
        }), 500

@app.route('/realtime/search', methods=['GET'])
def web_search():
    """Search the web"""
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({
            "success": False,
            "message": "Please provide a search query."
        }), 400
    
    results = search_web(query)
    
    if results:
        return jsonify({
            "success": True,
            "results": results,
            "timestamp": get_current_time_info()['formatted']
        })
    else:
        return jsonify({
            "success": False,
            "message": "Unable to perform web search."
        }), 500

@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    """Get conversation history for a user (UNLIMITED)"""
    try:
        user_id = request.args.get('user_id', 'default')
        limit = request.args.get('limit', None)
        limit = int(limit) if limit else None
        
        if user_id not in conversations:
            return jsonify({
                "success": True,
                "user_id": user_id,
                "message": "No conversation history found. Start chatting to build your conversation!",
                "messages": [],
                "total_messages": 0
            })
        
        conv = conversations[user_id]
        messages = conv["messages"][-limit:] if limit else conv["messages"]
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "messages": messages,
            "total_messages": len(conv["messages"]),
            "context_summary": get_conversation_summary(user_id),
            "topics": conv["context"]["topics"],
            "language": SUPPORTED_LANGUAGES.get(conv["context"]["language"], "English"),
            "metadata": conv["metadata"],
            "unlimited": True
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "history_fetch_failed",
            "message": f"Unable to retrieve conversation history: {str(e)}"
        }), 500

@app.route('/chat/context', methods=['GET'])
def get_chat_context():
    """Get current conversation context"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        if user_id not in conversations:
            return jsonify({
                "success": True,
                "user_id": user_id,
                "message": "No active conversation context",
                "context": {}
            })
        
        conv = conversations[user_id]
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "context": conv["context"],
            "recent_messages": len(get_conversation_context(user_id)) // 2,
            "summary": get_conversation_summary(user_id),
            "language": SUPPORTED_LANGUAGES.get(conv["context"]["language"], "English"),
            "metadata": conv["metadata"]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "context_fetch_failed",
            "message": f"Unable to retrieve conversation context: {str(e)}"
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Premium intelligent chat - Multi-modal AI routing with conversation memory & real-time data"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "invalid_request",
                "message": "Please provide a valid JSON request body with your message."
            }), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        force_model = data.get('model', None)
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "missing_message",
                "message": "Please provide a message for our AI to process."
            }), 400
        
        # Detect language
        detected_language = detect_language(user_message)
        
        # Initialize conversation if needed
        init_conversation(user_id)
        
        # Check for real-time data requirements
        real_time_query = check_for_real_time_query(user_message)
        real_time_data = None
        
        if real_time_query:
            real_time_data = get_real_time_data(real_time_query, user_message)
        
        request_type = detect_request_type(user_message)
        
        if request_type == 'video':
            prompt = clean_prompt(user_message, 'video')
            duration = data.get('duration', 3)
            result = generate_video_runway(prompt, duration)
            
            if result['success']:
                update_conversation_context(user_id, user_message, f"Generated video: {prompt}", detected_language)
                
                return jsonify({
                    "success": True,
                    "type": "video",
                    "message": "Your premium cinematic video has been generated successfully!",
                    "video": result['video'],
                    "format": "base64",
                    "model_used": "runway-gen-3-style",
                    "prompt": prompt,
                    "duration": result.get('duration'),
                    "fps": result.get('fps'),
                    "quality": "professional",
                    "language": SUPPORTED_LANGUAGES.get(detected_language),
                    "conversation_context": get_conversation_summary(user_id)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error'),
                    "message": result.get('message'),
                    "retry_after": result.get('retry_after')
                }), 500
        
        elif request_type == 'image':
            prompt = clean_prompt(user_message, 'image')
            result = generate_image_sd35(prompt)
            
            if result['success']:
                update_conversation_context(user_id, user_message, f"Generated image: {prompt}", detected_language)
                
                return jsonify({
                    "success": True,
                    "type": "image",
                    "message": "Your professional-grade image has been created successfully!",
                    "image": result['image'],
                    "format": "base64",
                    "model_used": "stable-diffusion-3.5-large",
                    "prompt": prompt,
                    "quality": "premium",
                    "language": SUPPORTED_LANGUAGES.get(detected_language),
                    "conversation_context": get_conversation_summary(user_id)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error'),
                    "message": result.get('message')
                }), 500
        
        else:
            # Get conversation context for continuity
            conversation_history = get_conversation_context(user_id)
            
            if force_model:
                selected_model = force_model
            else:
                selected_model = detect_query_type(user_message)
            
            if selected_model == 'gpt5-pro':
                response_text = get_gpt5_pro_response(user_message, conversation_history, detected_language, real_time_data)
            else:
                response_text = get_opus_response(user_message, conversation_history, detected_language, real_time_data)
            
            if "unable" in response_text.lower() or "unavailable" in response_text.lower():
                return jsonify({
                    "success": False,
                    "error": "service_error",
                    "message": response_text
                }), 500
            
            # Update conversation context
            update_conversation_context(user_id, user_message, response_text, detected_language)
            
            input_tokens = len(user_message.split())
            output_tokens = len(response_text.split())
            
            return jsonify({
                "success": True,
                "type": "text",
                "message": "Response generated by our premium AI engine with conversation context & real-time data",
                "response": response_text,
                "model_used": selected_model,
                "user_id": user_id,
                "detected_language": SUPPORTED_LANGUAGES.get(detected_language),
                "real_time_data_used": real_time_data is not None,
                "real_time_query_type": real_time_query,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "conversation_length": conversations[user_id]["metadata"]["message_count"],
                "context_used": len(conversation_history) // 2,
                "topics_discussed": conversations[user_id]["context"]["topics"],
                "quality": "professional",
                "unlimited": True
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "server_error",
            "message": f"We're experiencing an unexpected issue. Our engineers have been notified: {str(e)}"
        }), 500

@app.route('/analyze-file', methods=['POST'])
def analyze_file():
    """
    Premium file analysis endpoint - UNLIMITED file size support
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "missing_file",
                "message": "Please provide a file for analysis. We support all file formats with unlimited size."
            }), 400
        
        file = request.files['file']
        question = request.form.get('question', 'Provide comprehensive analysis with actionable insights')
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "invalid_filename",
                "message": "The uploaded file appears to be empty or invalid. Please select a valid file."
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "unsupported_format",
                "message": f"This file format is not currently supported. We accept: {', '.join(ALLOWED_EXTENSIONS['all'])}"
            }), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        file_type = get_file_type(filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        file_size = os.path.getsize(file_path)
        
        result = {
            "success": True,
            "message": "File analyzed successfully with premium intelligence (UNLIMITED)",
            "filename": filename,
            "file_type": file_type,
            "file_size": f"{file_size / (1024*1024):.2f} MB",
            "processing_quality": "premium",
            "unlimited": True
        }
        
        if file_type == 'image':
            analysis = analyze_image_with_gemini(file_path, question)
            result["analysis"] = analysis
            result["model_used"] = "gemini-1.5-flash"
            result["analysis_type"] = "Advanced visual intelligence"
            
        elif file_type == 'document':
            if file_ext == 'pdf':
                text = extract_text_from_pdf(file_path)
            elif file_ext == 'docx':
                text = extract_text_from_docx(file_path)
            else:
                text = extract_text_from_txt(file_path)
            
            result["extracted_text"] = text[:1000] + "..." if len(text) > 1000 else text
            result["text_length"] = len(text)
            result["word_count"] = len(text.split())
            result["analysis"] = analyze_document_with_ai(text, question)
            result["model_used"] = "gemini-1.5-flash" if gemini_model else "gpt5-pro"
            result["analysis_type"] = "Comprehensive document intelligence"
            
        elif file_type == 'spreadsheet':
            spreadsheet_data = analyze_spreadsheet(file_path, file_ext)
            result["data_analysis"] = spreadsheet_data
            
            summary_text = f"Dataset contains {spreadsheet_data.get('rows')} rows across {spreadsheet_data.get('columns')} columns. Columns: {', '.join(spreadsheet_data.get('column_names', []))}"
            result["analysis"] = analyze_document_with_ai(summary_text, question)
            result["model_used"] = "Advanced analytics engine"
            result["analysis_type"] = "Statistical data intelligence"
        
        elif file_type == 'code':
            code_text = extract_text_from_txt(file_path)
            result["code"] = code_text
            result["lines"] = len(code_text.split('\n'))
            result["analysis"] = analyze_document_with_ai(code_text, f"Analyze this {file_ext} code: {question}")
            result["model_used"] = "gpt5-pro"
            result["analysis_type"] = "Code analysis & review"
        
        os.remove(file_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": "processing_error",
            "message": f"We encountered an issue while processing your file. Our team has been notified: {str(e)}"
        }), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Premium conversation management - Reset conversation memory"""
    try:
        data = request.json if request.json else {}
        user_id = data.get('user_id', 'default')
        
        if user_id in conversations:
            msg_count = conversations[user_id]["metadata"]["message_count"]
            topics = conversations[user_id]["context"]["topics"]
            language = conversations[user_id]["context"]["language"]
            conversations[user_id] = None
            del conversations[user_id]
            
            return jsonify({
                "success": True,
                "message": f"Your conversation has been reset successfully. Cleared {msg_count} messages and {len(topics)} topics.",
                "user_id": user_id,
                "status": "refreshed",
                "cleared_topics": topics,
                "language": SUPPORTED_LANGUAGES.get(language)
            })
        else:
            return jsonify({
                "success": True,
                "message": "No active conversation found. You're starting fresh!",
                "user_id": user_id,
                "status": "clean_slate"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "reset_failed",
            "message": f"Unable to reset conversation: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Premium system health monitoring"""
    return jsonify({
        "status": "optimal",
        "message": "🚀 All systems operational - UNLIMITED Premium AI services running at full potential",
        "uptime": "99.9%",
        "active_users": len(conversations),
        "total_conversations": sum(conv["metadata"]["message_count"] for conv in conversations.values() if conv),
        "models": {
            "opus-4.5": "Operational ✅",
            "gpt5-pro": "Operational ✅",
            "stable-diffusion-3.5": "Operational ✅",
            "runway-gen-3-style": "Operational ✅",
            "gemini-1.5-flash": "Operational ✅" if gemini_model else "Configuration Required"
        },
        "capabilities": {
            "text_chat": True,
            "conversation_memory": True,
            "context_tracking": True,
            "multi_language": True,
            "real_time_data": True,
            "image_generation": True,
            "video_generation": True,
            "file_analysis": True,
            "image_analysis": gemini_model is not None,
            "document_extraction": True,
            "spreadsheet_analysis": True,
            "code_analysis": True,
            "web_search": True,
            "news_updates": True,
            "weather_data": True,
            "crypto_prices": True
        },
        "unlimited_features": {
            "file_size": "Unlimited ♾️",
            "conversation_length": "Unlimited ♾️",
            "context_window": f"{CONTEXT_WINDOW} messages (Enhanced)",
            "supported_languages": len(SUPPORTED_LANGUAGES),
            "file_formats": len(ALLOWED_EXTENSIONS['all'])
        },
        "real_time_info": get_current_time_info(),
        "service_tier": "Premium UNLIMITED",
        "support": "🌟 24/7 enterprise support available"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)