from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.websockets import websocket_endpoint
from app.api import voice, conversations, auth, calendar, system, emails, news, files
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Anime Model Chatbot API",
    description="Backend API for the Anime Model Chatbot application with Gemini AI and Voice Cloning",
    version="0.3.0",
)

@app.on_event("startup")
async def startup_event():
    """Preload model and cache on startup to speed up first request"""
    print("🚀 Starting up... Preloading XTTS model and character cache...")
    try:
        # Import the singleton voice_service instance
        from app.services.voice_service import voice_service
        
        # Use the new preload method
        voice_service.preload_model_if_needed()
        
    except Exception as e:
        print(f"⚠️ Startup preload warning: {e}")
        print("Voice service will still work, but first request may be slower")
        import traceback
        traceback.print_exc()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        os.getenv("FRONTEND_URL", "http://localhost:5173")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(conversations.router)
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(calendar.router, prefix="/api", tags=["calendar"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(emails.router, prefix="/api", tags=["emails"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(files.router, prefix="/api", tags=["files"])

@app.get("/")
async def root():
    return {
        "message": "Anime Model Chatbot Backend is running!",
        "ai_provider": "ollama",
        "ai_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3:latest"),
        "voice": "XTTS Voice Cloning",
        "character": "Suzune Horikita",
        "version": "0.5.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_service": "ollama",
        "model": os.getenv("OLLAMA_MODEL", "dolphin-llama3:latest"),
        "voice_service": "xtts",
        "character": "suzune_horikita"
    }

# Register the WebSocket endpoint
@app.websocket("/ws/chat/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str):
    await websocket_endpoint(websocket, user_id)