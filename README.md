# Anime Model Chatbot - Setup and Usage Instructions

This project is a full-stack AI chatbot application with a 3D character interface. The application consists of a Python FastAPI backend for handling WebSocket communications and a Vue.js frontend for displaying the interactive 3D character and chat interface.

## Project Structure

```
grok-anime-chatbot/
├── backend/                  # Python FastAPI backend
│   ├── app/                  # Application code
│   │   ├── api/              # API endpoints and WebSocket handlers
│   │   │   ├── websockets.py # WebSocket with AI + Voice
│   │   │   └── voice.py      # Voice API endpoints
│   │   ├── services/         # Business logic services
│   │   │   ├── gemini_service.py  # Google Gemini AI
│   │   │   └── voice_service.py   # XTTS Voice Cloning
│   │   ├── static/           # Static files
│   │   │   ├── voices/       # Character voice samples
│   │   │   └── temp_audio/   # Generated audio (auto-cleanup)
│   │   └── main.py          # FastAPI application entry point
│   ├── .env                 # Environment variables (API keys)
│   ├── requirements.txt     # Python dependencies
│   └── run.py              # Script to run the backend server
└── frontend/                # Vue.js frontend
    ├── public/              # Static assets
    │   └── avatar.vrm       # 3D character model (to be added)
    ├── src/                 # Source code
    │   ├── components/      # Vue components
    │   │   ├── camera/      # Camera view components
    │   │   ├── character/   # 3D character components
    │   │   ├── chat/        # Chat interface components
    │   │   └── layout/      # Layout components
    │   ├── services/        # JavaScript services
    │   │   └── websocket.js # WebSocket service
    │   ├── stores/          # Pinia stores
    │   │   └── chatStore.js # Chat state management
    │   ├── App.vue          # Main Vue component
    │   └── main.js          # JavaScript entry point
    ├── package.json         # NPM dependencies and scripts
    └── vite.config.js       # Vite configuration
```

## Prerequisites

1. Conda (Anaconda or Miniconda)
2. Git (optional, for cloning the repository)

## Setup Instructions

### Using Conda Environment (Recommended)

1. Set up the environment and install all dependencies:
   ```
   # On Windows
   setup.bat
   
   # On macOS/Linux
   bash setup.sh
   ```
   
   This script will:
   - Create a conda environment called `aniChatbot`
   - Install Python and Node.js in the environment
   - Install all backend and frontend dependencies

2. Add a VRM model:
   - You need to add a VRM model file to `frontend/public/avatar.vrm`
   - You can download free VRM models from sites like VRoid Hub or The Seed Online

3. Run the application:
   ```
   # On Windows
   run.bat
   
   # On macOS/Linux
   bash run.sh
   ```
   
   This will start both the backend server (http://localhost:8000) and the frontend development server (http://localhost:5173)

### Manual Setup (Alternative)

If you prefer to set up manually:

1. Create and activate a conda environment:
   ```
   conda env create -f environment.yml
   conda activate aniChatbot
   ```

2. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

3. Run the backend server:
   ```
   cd backend
   python run.py
   ```

4. Run the frontend development server (in a separate terminal):
   ```
   cd frontend
   npm run dev
   ```

## Usage Instructions

1. Open your browser and navigate to http://localhost:5173

2. The interface is divided into three main columns:
   - Left Column: Chat interface where you can send messages
   - Middle Column: 3D character that responds with expressions based on messages
   - Right Column: Camera feed with **real-time face detection and emotion recognition** (requires camera permission)

3. Type a message in the chat interface and press "Send" or hit Enter

4. The backend will process your message with Google Gemini AI and respond with:
   - **Intelligent AI responses** powered by Gemini 2.0 Flash
   - **Voice synthesis** using Suzune Horikita's voice (XTTS)
   - **Character expressions** based on detected emotions

5. **Voice Integration** 🎤
   - All AI responses are automatically spoken with Suzune Horikita's voice
   - Audio files are automatically cleaned up after 60 seconds
   - See [VOICE_SETUP.md](VOICE_SETUP.md) for voice configuration details

6. **Camera Emotion Detection** 📸
   - Real-time face detection using Google MediaPipe
   - Detects 6 emotions: Happy, Sad, Angry, Surprised, Blinking, Neutral
   - Displays emotion with emoji in cyberpunk-themed UI
   - Click "Enable Camera" in right panel to start
   - See [CAMERA_FEATURE_SUMMARY.md](CAMERA_FEATURE_SUMMARY.md) for quick guide
   - See [MEDIAPIPE_CAMERA_SETUP.md](MEDIAPIPE_CAMERA_SETUP.md) for detailed documentation

7. **Google Calendar Integration** 📅 **NEW!**
   - Automatic event creation from natural language
   - Detects date/time mentions in chat (e.g., "tomorrow I have a meeting at 8am")
   - Creates events in user's Google Calendar automatically
   - AI confirms event creation in response
   - See [CALENDAR_QUICKSTART.md](CALENDAR_QUICKSTART.md) for quick setup
   - See [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) for detailed guide

## Customization

### Character Model

To use a different VRM model:
1. Replace `frontend/public/avatar.vrm` with your preferred model
2. Ensure your model has the standard VRM expressions (happy, sad, angry, neutral)

### Backend Logic

To enhance the AI responses:
1. Modify `backend/app/api/websockets.py` to implement more sophisticated response logic
2. Consider integrating with a language model API for more natural conversations

### Frontend Design

To customize the UI appearance:
1. Edit the CSS in the Vue components
2. Modify the three-column layout in `frontend/src/components/layout/TheMainLayout.vue`

## Next Steps for Development

1. ✅ **COMPLETED:** AI conversation with Google Gemini
2. ✅ **COMPLETED:** Voice cloning with XTTS (Suzune Horikita)
3. ✅ **COMPLETED:** Frontend audio playback integration
4. ✅ **COMPLETED:** Camera face detection and emotion recognition (MediaPipe)
5. ✅ **COMPLETED:** Google Calendar integration with natural language event creation
6. 🔄 **OPTIONAL:** Sync camera emotions with character expressions (see [CAMERA_CHARACTER_SYNC.md](CAMERA_CHARACTER_SYNC.md))
7. Add more character animations and expressions
8. Add lip-sync for character model
9. Implement speech recognition for voice input
10. Implement user authentication
11. Add conversation history persistence

## Troubleshooting

### WebSocket Connection Issues

If you experience WebSocket connection problems:
1. Ensure both frontend and backend servers are running
2. Check the browser console for error messages
3. Verify the WebSocket URL in `frontend/src/services/websocket.js` matches your backend URL

### Character Model Issues

If the character model doesn't load properly:
1. Make sure the VRM model file exists at `frontend/public/avatar.vrm`
2. Check the browser console for Three.js errors
3. Try a different VRM model file to rule out model-specific issues

### General Issues

For other issues:
1. Check the console logs in both browser and terminal
2. Ensure all dependencies are correctly installed
3. Verify you're using compatible versions of Node.js and Python