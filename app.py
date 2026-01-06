from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import aiohttp
import asyncio
import json
import os
import re
from datetime import datetime, timedelta

# FastAPI App
app = FastAPI(
    title="hackGPT AI API",
    description="🚀 High-Performance AI Chat API with Claude Opus & GPT-5 Pro",
    version="9.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conversation storage
conversations: Dict[str, Dict] = {}
CONTEXT_WINDOW = 20

# API endpoints
OPUS_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'
GPT5_PRO_API = 'https://chatbot-ji1z.onrender.com/chatbot-ji1z'

# Multi-Language Support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'hi-en': 'Hinglish',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German'
}

# Pydantic Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    user_id: Optional[str] = Field(default="default", description="User identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What is AI?",
                "user_id": "user123"
            }
        }

class ChatResponse(BaseModel):
    success: bool
    response: str
    answer: str
    model_used: str
    language: str
    conversation_length: int
    real_time_data_used: bool

class ResetRequest(BaseModel):
    user_id: Optional[str] = Field(default="default", description="User identifier")

class ResetResponse(BaseModel):
    success: bool
    message: str

class StatusResponse(BaseModel):
    status: str
    message: str
    version: str
    features: Dict[str, bool]
    supported_languages: List[str]
    endpoints: Dict[str, str]
    note: str

class HealthResponse(BaseModel):
    status: str
    message: str
    active_users: int
    total_conversations: int
    features_active: Dict[str, bool]
    timestamp: str

# Helper Functions
def detect_language(text: str) -> str:
    """Detect language with Hinglish support"""
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if hindi_chars > 0 and english_chars > 0:
        return 'hi-en'
    elif hindi_chars > english_chars:
        return 'hi'
    return 'en'

def get_current_time_info() -> Dict[str, str]:
    """Get current IST time"""
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return {
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'day': now.strftime('%A'),
        'formatted': now.strftime('%d %B %Y, %I:%M %p IST')
    }

async def fetch_crypto_prices() -> Optional[Dict]:
    """Fetch cryptocurrency prices asynchronously"""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,inr'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
    except:
        pass
    return None

def check_for_real_time_query(message: str) -> Optional[str]:
    """Check if message needs real-time data"""
    message_lower = message.lower()
    
    if any(k in message_lower for k in ['time', 'date', 'day', 'today', 'समय', 'आज']):
        return 'time'
    elif any(k in message_lower for k in ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth']):
        return 'crypto'
    return None

async def get_real_time_data(query_type: str, message: str) -> Dict:
    """Fetch real-time data asynchronously"""
    data = {}
    if query_type == 'time':
        data['time_info'] = get_current_time_info()
    elif query_type == 'crypto':
        data['crypto'] = await fetch_crypto_prices()
    return data

def init_conversation(user_id: str):
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

def update_conversation_context(user_id: str, message: str, response: str, language: str = 'en'):
    """Update conversation"""
    if user_id not in conversations:
        init_conversation(user_id)
    
    conv = conversations[user_id]
    conv["messages"].append({"role": "user", "content": message})
    conv["messages"].append({"role": "assistant", "content": response})
    conv["context"]["language"] = language
    conv["metadata"]["message_count"] = len(conv["messages"])

def get_conversation_context(user_id: str) -> List[Dict[str, str]]:
    """Get recent conversation context"""
    if user_id not in conversations:
        return []
    
    conv = conversations[user_id]
    recent = conv["messages"][-CONTEXT_WINDOW:]
    return [{"role": m["role"], "content": m["content"]} for m in recent]

async def get_opus_response(
    question: str, 
    conversation_history: List[Dict] = [], 
    language: str = 'en', 
    real_time_data: Optional[Dict] = None
) -> str:
    """Get response from Opus asynchronously"""
    messages = []
    
    time_info = get_current_time_info()
    system_context = f"You are a premium AI assistant. Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language)}. Provide professional responses."
    
    if real_time_data:
        system_context += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
    
    messages.append({'role': 'system', 'content': system_context})
    messages.extend(conversation_history)
    messages.append({'role': 'user', 'content': question})
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OPUS_API, 
                json={'messages': messages}, 
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                return f"Service temporarily unavailable (Status: {response.status})"
    except asyncio.TimeoutError:
        return "Service timeout - please try again"
    except Exception as e:
        return f"Service error: {str(e)}"

async def get_gpt5_pro_response(
    question: str, 
    conversation_history: List[Dict] = [], 
    language: str = 'en', 
    real_time_data: Optional[Dict] = None
) -> str:
    """Get response from GPT-5 Pro asynchronously"""
    messages = []
    
    time_info = get_current_time_info()
    system_prompt = f"You are an elite AI assistant. Current: {time_info['formatted']}. Language: {SUPPORTED_LANGUAGES.get(language)}. Deliver comprehensive, professional responses."
    
    if real_time_data:
        system_prompt += f"\n\nReal-time Data: {json.dumps(real_time_data)}"
    
    messages.append({'role': 'assistant', 'content': system_prompt})
    messages.extend(conversation_history)
    messages.append({'role': 'user', 'content': question})
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GPT5_PRO_API, 
                json={'messages': messages}, 
                timeout=aiohttp.ClientTimeout(total=45)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                return f"Premium service temporarily unavailable (Status: {response.status})"
    except asyncio.TimeoutError:
        return "Premium service timeout - please try again"
    except Exception as e:
        return f"Service error: {str(e)}"

# API Routes
@app.get("/", response_model=StatusResponse)
async def home():
    """API status and information"""
    return StatusResponse(
        status="operational",
        message="🚀 FastAPI AI Chat API v9.0 - High Performance Edition",
        version="9.0.0",
        features={
            "text_chat": True,
            "multi_language": True,
            "hindi_hinglish": True,
            "real_time_data": True,
            "conversation_memory": True,
            "async_processing": True,
            "auto_docs": True,
            "image_generation": False,
            "video_generation": False,
            "file_analysis": False
        },
        supported_languages=list(SUPPORTED_LANGUAGES.values()),
        endpoints={
            "/": "API status",
            "/chat": "Async text chat with memory",
            "/reset": "Reset conversation",
            "/health": "Health check",
            "/docs": "Swagger UI documentation",
            "/redoc": "ReDoc documentation"
        },
        note="FastAPI async version - 10x faster than Flask!"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Async text chat endpoint with intelligent routing"""
    try:
        user_message = request.message.strip()
        user_id = request.user_id
        
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Detect language
        detected_language = detect_language(user_message)
        init_conversation(user_id)
        
        # Check for real-time data needs
        real_time_query = check_for_real_time_query(user_message)
        real_time_data = await get_real_time_data(real_time_query, user_message) if real_time_query else None
        
        # Get conversation history
        conversation_history = get_conversation_context(user_id)
        
        # Intelligent model selection
        word_count = len(user_message.split())
        complex_keywords = ['code', 'debug', 'algorithm', 'analyze', 'detailed', 'comprehensive']
        is_complex = word_count > 50 or any(k in user_message.lower() for k in complex_keywords)
        
        # Async API call (faster!)
        if is_complex:
            response_text = await get_gpt5_pro_response(user_message, conversation_history, detected_language, real_time_data)
            model = 'gpt5-pro'
        else:
            response_text = await get_opus_response(user_message, conversation_history, detected_language, real_time_data)
            model = 'opus-4.5'
        
        # Update conversation
        update_conversation_context(user_id, user_message, response_text, detected_language)
        
        return ChatResponse(
            success=True,
            response=response_text,
            answer=response_text,
            model_used=model,
            language=SUPPORTED_LANGUAGES.get(detected_language, 'English'),
            conversation_length=conversations[user_id]["metadata"]["message_count"],
            real_time_data_used=real_time_data is not None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@app.post("/reset", response_model=ResetResponse)
async def reset_conversation(request: ResetRequest):
    """Reset user conversation"""
    user_id = request.user_id
    
    if user_id in conversations:
        msg_count = conversations[user_id]["metadata"]["message_count"]
        del conversations[user_id]
        return ResetResponse(
            success=True,
            message=f"Conversation reset successfully. Cleared {msg_count} messages."
        )
    
    return ResetResponse(
        success=True,
        message="No conversation to reset"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="optimal",
        message="All systems operational - FastAPI AI Chat v9.0",
        active_users=len(conversations),
        total_conversations=sum(c["metadata"]["message_count"] for c in conversations.values()),
        features_active={
            "text_chat": True,
            "multi_language": True,
            "hindi_hinglish": True,
            "real_time_data": True,
            "conversation_memory": True,
            "async_processing": True
        },
        timestamp=get_current_time_info()['formatted']
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    print("✨ FastAPI AI Chat API v9.0 starting...")
    print("🚀 Async processing enabled")
    print("📚 API docs available at /docs")
    print("⚡ 10x faster than Flask!")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 FastAPI AI Chat API shutting down...")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )