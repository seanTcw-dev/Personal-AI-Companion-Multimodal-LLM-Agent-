# 🤖 AI Anime Chatbot (VirtuAI Companion)

A full-stack, interactive AI chatbot featuring a 3D anime character interface, real-time emotion detection, voice cloning, and smart assistant capabilities.

![Banner Image Placeholder](frontend/public/banner_placeholder.png)

## 🌟 Key Features

*   **3D Character Interface**: Interactive VRM character (default: Suzune Horikita) that reacts to conversations with expressions and animations.
*   **Intelligent AI**: Powered by **Google Gemini 2.0 Flash** for natural, context-aware conversations.
*   **Voice Cloning (XTTS)**: High-quality, real-time text-to-speech using custom voice models.
*   **Dual Emotion Detection**:
    *   **Camera 📹**: Real-time facial expression analysis using MediaPipe (Happy, Sad, Angry, Surprised, Neutral).
    *   **Audio 🎤**: Detects emotional sounds like laughter, gasps, and sighs to trigger immediate AI responses.
*   **Smart Assistant**:
    *   **Google Calendar 📅**: Natural language event creation (e.g., "Schedule a meeting for tomorrow at 2 PM").
*   **Cyberpunk UI**: Modern, responsive interface with real-time visualizations.

---

## 🛠️ Project Structure

```
grok-anime-chatbot/
├── backend/                  # Python FastAPI backend
│   ├── app/                  # Application core
│   │   ├── api/              # Endpoints (WebSocket, Voice, Calendar)
│   │   ├── services/         # Logic (Gemini, XTTS, Calendar)
│   │   └── static/           # Voice samples & temp audio
│   ├── run.py                # Server entry point
│   └── requirements.txt      # Python dependencies
└── frontend/                 # Vue.js 3 + Vite frontend
    ├── public/               # Static assets (avatar.vrm)
    ├── src/
    │   ├── components/       # UI Components (3D, Chat, Camera)
    │   ├── services/         # WebSocket & API services
    │   └── stores/           # Pinia State Management
    └── index.html            # Entry HTML
```

---

## 🚀 Quick Start (Recommended)

### Prerequisites
*   **OS**: Windows (Recommended for batch scripts), macOS, or Linux.
*   **Conda**: Anaconda or Miniconda installed.
*   **Hardware**: Webcam (for face detection) and Microphone (for audio analysis).

### 1-Click Installation
Simply run the automatic installer script from the root directory:

```cmd
install-all.bat
```

This will:
1.  Create a Conda environment `aniChatbot`.
2.  Install Python dependencies (FastAPI, PyTorch, etc.).
3.  Install Node.js and frontend dependencies.

### Running the App
Start both backend and frontend servers with one command:

```cmd
start.bat
```

*   **Frontend**: [http://localhost:5173](http://localhost:5173)
*   **Backend**: [http://localhost:8000](http://localhost:8000)

---

## ⚙️ Configuration

### 1. Environment Secrets
Create a `.env` file in the `backend/` directory:

```env
# backend/.env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_oauth_client_id
GOOGLE_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback
```

### 2. Google Calendar Setup
To enable calendar scheduling:
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable **Google Calendar API**.
3.  Create **OAuth 2.0 Credentials** (Web Application).
4.  Download the JSON secret and place it in `backend/credentials/client_secret.json`.

### 3. Custom 3D Model
1.  Get a `.vrm` file (from VRoid Hub, etc.).
2.  Rename it to `avatar.vrm`.
3.  Place it in `frontend/public/avatar.vrm`.

---

## 🎮 Usage Guide

### Chat & Interaction
1.  open [http://localhost:5173](http://localhost:5173).
2.  **Type** in the chat box to talk to the AI.
3.  The character will **speak back** using the cloned voice and **change expressions** based on the context.

### Emotion Detection
1.  Click **"Enable Camera"** in the right panel.
2.  Allow camera permissions.
3.  The AI will detect your face emotions (e.g., if you smile, the AI might smile back!).
4.  Toggle **"Mic: OFF"** to **"Mic: ON"** to enable audio emotion detection (laughter, sighs).

### Calendar Commands
Try sending messages like:
*   *"Schedule a dentist appointment for next Monday at 10 AM."*
*   *"Remind me to call John tomorrow morning."*
*   *"I have a meeting on Friday at 2 PM."*

The AI will parse the date/time and confirm the creation of the event in your Google Calendar.

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Connection Failed** | Ensure `start.bat` is running and keeping both terminal windows open. Check `frontend/src/services/websocket.js` URL. |
| **Model Not Loading** | Verify `frontend/public/avatar.vrm` exists. Check browser console (F12) for Three.js errors. |
| **Microphone Issues** | Check browser stats/permissions. Ensure HTTPS or localhost is used. Chrome/Edge recommended. |
| **Calendar Error** | Check `backend/credentials/client_secret.json` path and `.env` variables. Re-authorize via the UI if link is provided. |

---

## 📜 Documentation Index
For deeper dives into specific features, check the dedicated guides:

*   [📅 Google Calendar Setup](GOOGLE_CALENDAR_SETUP.md)
*   [🎤 Audio Emotion Detection](AUDIO_EMOTION_DETECTION.md)
*   [📹 Camera Setup](MEDIAPIPE_CAMERA_SETUP.md)
*   [🔊 Voice Configuration](VOICE_SETUP.md)

---

**Developed with ❤️ by [Your Name]**
