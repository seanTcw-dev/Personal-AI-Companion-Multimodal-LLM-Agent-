# 🤖 VirtuAI Companion — Multimodal LLM Agent with 3D Anime Interface

A full-stack, privacy-first AI companion featuring a reactive 3D anime character, real-time multimodal emotion detection, local voice cloning, and smart assistant tools — all running **100% locally** on your machine.

> **No cloud APIs for AI inference.** Your conversations, your data, your hardware.

---

## ✨ Highlights

| Feature | Description |
| :--- | :--- |
| 🧠 **Local LLM Brain** | Powered by [Ollama](https://ollama.com/) (Llama 3.2 / Gemma 3) running on WSL — zero API costs, complete privacy |
| 🎭 **3D Anime Avatar** | VRM character rendered with Three.js — lip-sync, emotion expressions, and Mixamo animations |
| 🗣️ **Voice Cloning** | Local [XTTS-v2](https://github.com/coqui-ai/TTS) engine — clone any voice from a 10-second WAV sample |
| 📹 **Facial Emotion Detection** | Real-time webcam analysis via MediaPipe — the avatar mirrors your expressions |
| ✋ **Gesture Control** | Hand gesture recognition to mute, stop speech, take screenshots, and close tabs |
| 🎤 **Audio Emotion Detection** | Microphone monitors laughs, sighs, and vocal cues with 3-layer loop prevention |
| 📅 **Smart Tools** | Google Calendar, daily briefings, file management, PDF analysis, web navigation |
| 🤖 **Telegram Bot** | Chat with your AI remotely from mobile via Telegram |
| 🖥️ **Desktop Pet Mode** | Transparent floating window — the character walks across your desktop |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Frontend (Vue.js 3 + Vite)                              │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Three.js│ │ MediaPipe│ │  Chat UI │ │Desktop Pet  │  │
│  │ VRM 3D  │ │ Face/Hand│ │ WebSocket│ │ Mode        │  │
│  └────┬────┘ └────┬─────┘ └─────┬────┘ └─────────────┘  │
│       └───────────┴─────────────┘                        │
│                     │ WebSocket                          │
├─────────────────────┼────────────────────────────────────┤
│  Backend (Python FastAPI)        │                        │
│  ┌─────────┐ ┌──────────┐ ┌─────┴─────┐ ┌────────────┐  │
│  │AI Router│ │Voice XTTS│ │ Tool Exec │ │Telegram Bot│  │
│  │(Intent) │ │(Cloning) │ │(Calendar) │ │(Remote)    │  │
│  └────┬────┘ └──────────┘ └───────────┘ └────────────┘  │
│       │                                                  │
├───────┼──────────────────────────────────────────────────┤
│  Local AI (WSL Ubuntu)                                   │
│  ┌────┴────┐                                             │
│  │ Ollama  │  llama3.2:3b / gemma3:4b                    │
│  │ (GPU)   │                                             │
│  └─────────┘                                             │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
├── backend/                  # Python FastAPI server
│   ├── app/
│   │   ├── api/              # WebSocket, Voice, Calendar endpoints
│   │   ├── config/           # System settings & persona config
│   │   ├── services/         # Core logic: LLM routing, Ollama, XTTS, Telegram
│   │   ├── tools/            # JSON tool definitions (calendar, briefing, files)
│   │   └── main.py           # FastAPI app
│   ├── run.py                # Entry point (starts FastAPI + Telegram Bot)
│   └── .env                  # Environment variables (not committed)
├── frontend/                 # Vue.js 3 + Vite
│   ├── public/
│   │   ├── animations/       # Mixamo FBX animations
│   │   ├── models/           # VRM 3D character (avatar.vrm)
│   │   └── sounds/           # UI sound effects
│   └── src/
│       ├── components/       # Camera, Character, Chat, Layout components
│       ├── services/         # WebSocket, API clients
│       ├── stores/           # Pinia state management
│       └── views/            # Pages: Chat, Settings, Landing, DesktopPet
├── requirements.txt          # Python dependencies
└── .gitignore
```

---

## 🚀 Quick Start

### Prerequisites

- **Windows** with [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install) (Ubuntu)
- **Conda** (Anaconda or Miniconda)
- **Ollama** installed inside WSL — [install guide](https://ollama.com/download/linux)
- **NVIDIA GPU** with CUDA support (recommended for XTTS voice cloning)
- Webcam & Microphone

### 1. Clone & Install

```bash
git clone https://github.com/seanTcw-dev/Personal-AI-Companion-Multimodal-LLM-Agent-.git
cd Personal-AI-Companion-Multimodal-LLM-Agent-
```

**Backend:**
```bash
conda create -n aniChatbot python=3.10 -y
conda activate aniChatbot
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `backend/.env`:
```env
# Ollama (running in WSL)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your_token_here

# Google Calendar (optional)
GOOGLE_API_KEY=your_key
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback
```

### 3. Pull a Model in WSL

```bash
# Inside WSL terminal
ollama pull llama3.2:3b
```

### 4. Run

**Start Ollama in WSL:**
```bash
ollama serve
```

**Start Backend** (new terminal):
```bash
conda activate aniChatbot
cd backend
python run.py
```

**Start Frontend** (new terminal):
```bash
cd frontend
npm run dev
```

| Service | URL |
| :--- | :--- |
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |

---

## 🎮 Usage

| Action | How |
| :--- | :--- |
| **Chat** | Type in the chat panel — AI responds with text + voice |
| **Voice Cloning** | Place a 10s+ `.wav` file in `backend/app/static/voices/` |
| **Emotion Detection** | Click "Enable Camera" — the avatar mirrors your expressions |
| **Gesture: Stop Speech** | Show open palm ✋ to the camera |
| **Gesture: Mute Toggle** | Point up ☝️ |
| **Gesture: Screenshot** | Victory sign ✌️ |
| **Gesture: Close Tab** | Closed fist 👊 |
| **Calendar** | _"Schedule a meeting tomorrow at 2 PM"_ |
| **Daily Briefing** | _"Give me today's briefing"_ |
| **Web Navigation** | _"Open YouTube"_ |
| **Telegram** | Message your bot on Telegram for remote access |

---

## 🔧 Customization

### Custom 3D Model
Place your `.vrm` file at `frontend/public/models/avatar.vrm`.

### Custom Voice
1. Record a clean 10-15 second voice sample (`.wav`, 24000 Hz)
2. Place it in `backend/app/static/voices/`
3. The XTTS-v2 engine will automatically clone the voice on startup

### Change LLM Model
Edit `OLLAMA_MODEL` in `backend/.env` to any model available via Ollama (e.g., `gemma3:4b`, `mistral`).

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| Frontend | Vue.js 3, Vite, Three.js, @pixiv/three-vrm, MediaPipe |
| Backend | Python, FastAPI, WebSockets |
| AI/LLM | Ollama (local), Llama 3.2 / Gemma 3 |
| Voice | Coqui XTTS-v2 (local voice cloning) |
| 3D Assets | VRM format, Mixamo FBX animations |
| Bot | python-telegram-bot |
| Auth | Google OAuth 2.0 |

---

## 📄 License

This project was developed as a **Final Year Project (FYP)**. All rights reserved.

---

<p align="center">
  Built with ❤️ using local AI — no cloud, no latency, no compromises.
</p>