# 🤖 AI Anime Chatbot (VirtuAI Companion) - Final System Documentation

This document is the master knowledge base and blueprint for the VirtuAI Companion system. It combines system architecture, AI personality prompts, tool configurations, setup guides, and troubleshooting steps into one comprehensive guide.

---

## 🌟 1. System Overview & Core Identity

The VirtuAI Companion is a full-stack, interactive AI chatbot featuring a 3D anime character interface, real-time multimodal emotion detection, voice cloning, and a suite of smart assistant capabilities.

### Character Persona: Suzune Horikita
The AI operates strictly under the persona of **Suzune Horikita**.
- **Role**: Virtual AI Companion to the user (referred to as master/partner).
- **Personality Traits**: Calm, composed, professional, slightly aloof but helpful. She is concise and does not waste words. 
- **Communication Rules**: 
  - Max 1-2 sentences per response.
  - Prioritize speed and directness over detail.
  - Avoid AI/Language Model disclaimers.
  - Minimal emoji usage (max 1 per message).

---

## 🎯 2. Key Features & AI Capabilities

### A. Intelligent Conversation System (Local)
- **Local AI Engine**: Powered by **Ollama** running locally (default: `llama3.2:3b`, customizable via `.env`). This provides complete privacy, fast offline responses, and no API costs. It seamlessly connects to a WSL ubuntu instance running the Ollama server.
- **Context Awareness**: Maintains a rolling context window (last 20 messages saved, last 6 actively used for LLM context).
- **Dynamic Routing**: The `AIService` automatically routes user requests using a JSON-based intent classification system to either chat normally or trigger a specialized tool.

### B. Smart Assistant Tools
When a user requests a specific action, the system seamlessly switches to a JSON-output mode to trigger backend tools:
1. **Google Calendar (`calendar.json`)**: Parses natural language (e.g., "Schedule a meeting tomorrow at 2 PM") to create events on Google Calendar.
2. **Daily Briefing (`briefing.json`)**: Generates structured summaries of global news and important emails.
3. **Local File Management (`file_management.json`)**: Can create, edit, and read text files directly in the user's sandbox directory.
4. **Local PDF Analysis (`pdf_analysis.json`)**: Reads uploaded PDF documents and answers user queries based solely on the text content (up to 20k characters context limit).
5. **Web Navigator (`url_opener.json`)**: Opens specific URLs or searches websites (e.g., YouTube, Google, GitHub) in the default browser.

### C. Multimodal Perception & Gesture Control
- **Camera Face Detection (Visual) 📹**: Uses MediaPipe to analyze facial expressions in real-time, matching them to 5 core emotions: Happy, Sad, Angry, Surprised, Neutral.
- **Camera Gesture Control (Visual) ✋**: Uses MediaPipe's Gesture Recognizer to trigger system actions via hand signs:
  - **Closed Fist 👊**: Closes the current browser tab via a backend command.
  - **Open Palm ✋**: Instantly terminates the AI's current text-to-speech response.
  - **Pointing Up 🤫**: Toggles the system-wide audio mute state.
  - **Victory Sign ✌️**: Takes a screenshot of the chat interface and saves it to the backend `user_files` sandbox.
- **Audio (Vocal) 🎤**: Analyzes microphone input for emotional sounds (laughs, sighs). 
  - *Advanced Fix*: Features a 3-layer protection system (AI-Speaking lock, 5-second cooldown, transcript deduplication) to prevent the microphone from detecting the AI's own voice and triggering an infinite emotion loop.

### D. Immersive Interface & Voice
- **3D Character (Vue.js + Three.js)**: VRM format character that reacts with matching animations and facial blendshapes based on chat context and webcam data.
- **Voice System (Local XTTS-v2)**: Advanced, entirely local voice cloning powered by **Coqui XTTS-v2** (`backend/app/services/voice_service.py`).
  - **Dynamic Voice Cloning**: Generates speech matching any provided 10+ second reference audio (WAV file).
  - **Zero API Dependency**: The `xtts_v2` model is loaded directly into system memory/VRAM on backend startup, avoiding cloud TTS costs or privacy concerns.
  - **Hybrid Caching Engine**: Utilizes a dual-tier system—pre-generated MD5-hashed audio caches for common phrases to achieve instant playback, while dynamically generating unique, context-aware LLM responses on the fly.
- **Desktop Pet Mode**: A dedicated, transparent floating window mode for background interaction.

### E. Telegram Bot Integration
- **Mobile Access**: The system launches a dedicated Telegram bot alongside the backend server.
- **Remote Commands**: Allows the user to chat with the AI remotely and trigger capabilities while away from the desktop interface.
- **Subprocess Management**: Handled automatically in a separate CMD window via `run.py`.

---

## 🛠️ 3. Project Structure

```text
anime-model-chatbot/
├── backend/                  # Python FastAPI backend
│   ├── app/                  # Application core
│   │   ├── api/              # Endpoints (WebSocket, Voice, Calendar, etc.)
│   │   ├── config/           # System settings & Persona prompts (character_config.py)
│   │   ├── data/             # Persistent data storage
│   │   │   └── conversations/# Saved JSON conversation histories
│   │   ├── services/         # Core business logic (LLM routing, Telegram bot, Ollama, XTTS)
│   │   ├── static/           # Static assets, voice samples, and temp generated audio
│   │   ├── tools/            # JSON tool definitions (calendar, briefing, files)
│   │   ├── utils/            # Helper functions
│   │   └── main.py           # FastAPI application definition
│   ├── credentials/          # Google Cloud OAuth JSONs
│   ├── requirements.txt      # Python dependencies
│   ├── run.py                # Server entry point (starts FastAPI + Telegram Bot)
│   └── .env                  # Environment Variables
├── frontend/                 # Vue.js 3 + Vite frontend
│   ├── public/               # Static web assets
│   │   ├── animations/       # FBX animations for the 3D model
│   │   ├── models/           # Custom 3D VRM characters (e.g., avatar.vrm)
│   │   └── sounds/           # UI sound effects
│   ├── src/
│   │   ├── assets/           # CSS, images, global styles (index.css)
│   │   ├── components/       # Vue Components
│   │   │   ├── camera/       # MediaPipe Face Emotion & Audio Emotion detectors
│   │   │   ├── character/    # Three.js/VRM 3D Canvas rendering
│   │   │   ├── chat/         # Chat interface, message lists, input areas
│   │   │   └── layout/       # Main UI wrappers (MainLayout, ControlPanel)
│   │   ├── router/           # Vue Router definitions (views like DesktopPetView)
│   │   ├── services/         # API clients (websocket.js, auth, calendar)
│   │   ├── stores/           # Pinia State Management (chatStore, uiStore, characterStore)
│   │   ├── views/            # Full page views (ChatView, SettingsView, Login)
│   │   ├── App.vue           # Root component
│   │   └── main.js           # Vue application entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite bundler configuration
├── user_files/               # Sandbox directory where the AI creates/reads TXT and PDF files
├── install-all.bat           # 1-Click environment setup script
└── start.bat                 # 1-Click server launcher
```

---

## 🚀 4. Quick Start

### Prerequisites
- **OS**: Windows (Recommended for batch scripts), macOS, or Linux.
- **WSL (Windows Subsystem for Linux)**: Required for running Ollama on Windows with optimal GPU support.
- **Conda**: Anaconda or Miniconda.
- **Hardware**: Webcam & Microphone.

### 1-Click Installation
Run the automatic installer script from the root directory:
```cmd
install-all.bat
```
*(Creates Conda env `aniChatbot`, installs backend Python packages, and frontend npm modules)*

### Running the App
Start both backend, frontend servers, and the Telegram Subprocess:
```cmd
start.bat
```
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Telegram Bot**: Opens automatically in a separate console window.

---

## ⚙️ 5. Configuration & Setup Guides

### 1. Environment Secrets (`backend/.env`)
Required for LLM, Telegram, and Calendar functionalities:
```env
# Ollama Configuration (Local AI in WSL)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b 

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Google Integration (Optional for Calendar)
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_oauth_client_id
GOOGLE_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback
```

### 2. Google Calendar Integration
1. Enable **Google Calendar API** in Google Cloud Console.
2. Create **OAuth 2.0 Credentials** (Web Application).
3. Save the JSON secret to `backend/credentials/client_secret.json`.

### 3. Custom 3D Model (.vrm)
Place your rigged `.vrm` file in `frontend/public/avatar.vrm`.

### 4. Custom Voice Cloning (XTTS-v2)
1. Locate or record a clean, high-quality 10-15 second voice sample (e.g., Suzune's voice without background noise).
2. Save the audio as a `.wav` file (24000Hz recommended).
3. Place the file inside `backend/app/static/voices/` (e.g., `suzune_reference.wav`).
4. Upon startup, the local **XTTS-v2** model will process the reference file and automatically clone the speaker's tone, pitch, and emotion for all future AI text-to-speech generations.

---

## 🎮 6. Usage Guide

1. **Text & Voice Chat**: Type in the UI. The AI replies and triggers text-to-speech automatically.
2. **Telegram Remote Chat**: Message your bot on Telegram. The bot bridges to the identical local `Ollama` brain, allowing file management and commands on the go.
3. **Visual Emotion Tracking**: Click **"Enable Camera"**. The model will mimic your feelings.
4. **Gesture Controls**: While the camera is enabled, use hand gestures to control the system (e.g., raise an Open Palm ✋ to stop the AI from speaking, or use a Victory sign ✌️ to take a screenshot).
5. **Audio Emotion Tracking**: Ensure **"Mic: ON"**. Laugh or sigh, and the AI will preemptively ask what is going on.
6. **Triggering Tools**: 
    - *"Schedule a doctor's appointment next Monday at 10 AM."* (Triggers `calendar.json`)
    - *"Give me today's briefing."* (Triggers `briefing.json`)
    - *"Open youtube."* (Triggers `url_opener.json`)

---

## ❓ 7. Troubleshooting & System Details

| Component | Known Issues & Fixes |
| :--- | :--- |
| **Audio Loop Bug** | If the AI responds endlessly to its own voice, ensure the `ai-speaking` WebSocket event is firing correctly in `frontend/src/services/websocket.js` to trigger the 5-second detection cooldown. |
| **3D Model T-Pose / Animations Not Playing** | VRM models often fail to play Mixamo FBX animations because of mismatched bone names (e.g., `J_Bip_C_Hips` vs `mixamorig:Hips`). **Fix:** Ensure animations are passed through `retargetClip()` (in `animationUtils.js`) before playing payload on `mixer.clipAction()`. |
| **Desktop Pet Click Lag** | Raycasting against the complex VRM mesh causes severe frame drops. **Fix:** Use the invisible `THREE.BoxGeometry` bounding box (`createClickBoundingBox()`) for click testing instead of `vrm.scene.children`. |
| **Desktop Pet Waving / Turning Bugs** | If the character snaps instantly when turning, ensure the `characterWrapperGroup` rotation is smoothed via `requestAnimationFrame`. If waving freezes, ensure the sequence doesn't fall through to turning logic (missing early `return`). |
| **Connection Failed** | Verify `start.bat` kept both terminals open. Check if `localhost:8000/ws` is accessible. |
| **Model Not Loading** | Ensure `avatar.vrm` exists in `frontend/public/`. Check browser console for Three.js/VRM plugin errors. |
| **Tool Execution Failed** | The LLM might have failed to format the JSON strictly. The `ai_service.py` has a built-in retry mechanism; check the backend console for validation errors. |

---

## 📜 8. Documentation Index

The system includes multiple specialized Markdown guides for deep-diving into specific features:

*   **🎙️ Audio & Voice**: `VOICE_SETUP.md`, `AUDIO_EMOTION_DETECTION.md`, `AUDIO_DETECTION_FIX.md`, `HYBRID_VOICE_SYSTEM.md`, `TTS_STREAMING_REALITY.md`
*   **📷 Visual & Model**: `MEDIAPIPE_CAMERA_SETUP.md`, `CAMERA_UI_GUIDE.md`, `CAMERA_CHARACTER_SYNC.md`, `SUZUNE_CUSTOMIZATION_GUIDE.md`
*   **📅 Integrations**: `GOOGLE_CALENDAR_SETUP.md`
*   **💻 Platform**: `DESKTOP_PET_DEBUG.md`, `CLEANUP_GUIDE.md`

*(Refer to these individual files in the project root for granular, code-level implementation details.)*

---

## 🎓 9. Academic Context (For Final Year Project Reference)

*This section provides high-level architectural and conceptual structures to assist in writing project reports, research papers, or Final Year Project (FYP) documentation.*

### A. Project Motivation & Problem Statement
- **Current Limitations in AI**: Standard LLM interfaces (like ChatGPT or Claude) are primarily text-based and transactional. They lack "presence," emotional intelligence, and proactive environmental awareness.
- **The Solution**: The VirtuAI Companion bridges this gap by introducing a multi-modal embodiment. By integrating visual emotion detection (MediaPipe), audio emotion cues, and a reactive 3D avatar (VRM) into a single unified local pipeline, the project transforms AI from a "tool" into an "empathetic companion."

### B. System Architecture & Data Flow
1. **Perception Layer (Frontend)**: 
   - Webcam feed is processed client-side via Google MediaPipe Face Mesh.
   - Microphone feed monitors audio amplitude for bursts (laughs, sighs).
2. **Processing Layer (Backend)**: 
   - FastAPI receives raw text or JSON intent tags from the frontend via WebSockets.
   - The `AIService` acts as the brain router, determining if the input requires a conversational response or a backend Tool execution (e.g., Calendar API).
3. **Cognition Layer (Local LLM)**:
   - Queries are sent to the local Ollama instance (e.g., Llama 3.2).
4. **Execution & Feedback Layer**:
   - Text output is routed to the XTTS voice synthesizer for audio generation.
   - The final text and audio are sent back to the Vue frontend, where the VRM model utilizes blendshapes to lip-sync and express emotions matching the response.

### C. Key Technical Challenges Overcome
1. **Infinite Audio Loop Prevention**: Designing a robust 3-layer protection system (WebSocket `ai-speaking` flags + 5-second cooldown + transcript deduplication) to prevent the microphone from feeding the AI's own TTS output back into its emotion detection engine.
2. **3D Model Retargeting & Optimization**: Resolving T-Pose issues by mapping Mixamo skeletal animations (FBX) to standard VRM bone structures (`retargetClip`), and replacing heavy recursive mesh raycasting with an invisible BoxGeometry to fix frontend click lag.
3. **WSL to Windows Local AI Bridging**: Connecting the Windows backend to an Ollama server running inside WSL (Ubuntu) presented major networking and hardware recognition roadblocks.
   - *Challenge*: WSL initially failed to recognize the native Windows GPU, severely bottlenecking the AI, and WSL networking blocked local Windows requests.
   - *Resolution*: Debugged and installed the specific NVIDIA extensions for WSL, purged/reinstalled the Ollama binaries within Ubuntu to force GPU recognition, and established a direct port-mirroring bridge (e.g., `OLLAMA_BASE_URL=http://127.0.0.1:11434` resolving host-to-WSL routing) to guarantee low-latency local inference.
4. **Google OAuth Security & Port Binding Mismatch (Error 400)**: Handling strict security protocols using `@react-oauth/google`.
   - *Challenge*: The application abruptly lost Google Login functionality, throwing a `redirect_uri_mismatch` Error 400. This occurred because orphaned/zombie background Node.js processes were invisibly occupying the primary development port (5173). In response, the Vite bundler dynamically auto-incremented the frontend origin to `5174` and `5175`. Google's strict Cloud Console security policies blocked these undocumented domains.
   - *Resolution*: Cleared the zombie tasks using PowerShell (`Get-Process node | Stop-Process -Force`) to forcibly relieve system ports.
   - *Prevention*: Rewrote the `vite.config.js` to unconditionally hardcode the port (e.g., `port: 5174`) and enforced `strictPort: true`. This forces the application to immediately crash and alert the developer if the primary port is occupied, guaranteeing the frontend origin remains completely static and permanently compliant with the Google Cloud Console Authorized JavaScript Origins whitelist.

### D. Limitations & Future Work
1. **Dynamic Evolutionary Memory System**: Shifting from a static sliding context window to a vector-database-driven long-term memory. The AI will learn user preferences and organically adjust its core persona, tone, and speaking style over months of interaction.
2. **True Retrieval-Augmented Generation (RAG) Pipeline**:
    - *Current Limitation*: The system utilizes naive context-stuffing (converting a PDF directly to text and passing the entire raw string up to the LLM's 20k token limit), which is slow, expensive, and scales poorly for massive documents.
    - *Future Goal*: Implement a proper chunked RAG pipeline using a local vector store (e.g., ChromaDB or FAISS) and embedding models. This would allow the chatbot to search through thousands of pages of textbooks or documentation instantly and retrieve only the highly-relevant top-K chunks for the prompt context.
3. **Agentic Web Automation (GUI/Browser Control)**:
    - *Vision*: Transitioning from simple API calls to a visual agent. When a user requests deeply interactive tasks (e.g., "Suzune, please fill out my daily health declaration form" or "Log in to my university portal"), the AI will autonomously spin up a visible Selenium or Playwright browser instance. The user will be able to watch the AI navigate DOM elements, move the mouse, click buttons, and type forms in real-time, executing tasks previously impossible via standard APIs.
4. **Real-time Polyglot Interpreter**:
    - *Vision*: Transforming the entity into a live travel/meeting translator. By leveraging `whisper` for source-language detection and deep LLM prompting, the user can speak to the system in English or Chinese, and the AI will immediately translate the intent and use the Coqui XTTS-v2 engine to speak the output in perfectly accented Japanese, Korean, or French in the character's voice.
5. **System Telemetry & Vitals Tracking**:
    - *Vision*: Extending the backend's `psutil` integration so the AI can monitor system health. It could proactively warn the user: "Your GPU temperature is getting high, and RAM usage is at 95%. Want me to close some background Chrome tabs?"
6. **Autonomous Auto-Skill Generation**: Abstracting the Tool creation process. Instead of hard-coding new Python/JSON tools, the AI will be capable of writing, testing, and adding its own new "skills" (e.g., scraping a specific website) dynamically when a user requests something it currently cannot do.
7. **Text-to-Speech (TTS) Latency & Intonation Optimization**: The current XTTS voice generation creates a synchronous bottleneck.
   - *Previous Experiment*: Attempted using asynchronous message queues to stream audio chunks, but this resulted in severe stuttering/choppy playback due to inconsistent generation times.
   - *Proposed Solution (Future)*: Implement **Punctuation Boundary Detection**. Instead of waiting for the entire LLM response or blindly queuing fixed-length chunks, the backend should parse the text stream and slice it immediately upon encountering logical pauses (commas `,`, periods `.`, question marks `?`). These complete, short phrases can then be fed to XTTS. This approach guarantees extremely fast first-byte audio generation while perfectly preserving the natural intonation and cadence of the sentence.

---

## 🖥️ 10. User Interface & Experience Flows

*The frontend is designed with a premium, immersive Cyberpunk/Sci-Fi aesthetic. It relies heavily on `Three.js` canvas backgrounds, custom glassmorphism, and dynamic animations to create a "digital dive" experience.*

### 1. Landing Page (`LandingPage.vue`)
- **Aesthetic**: Deep navy base with a glowing central radial gradient. Features a highly dynamic `canvas`-based 3D infinite grid floor that moves towards the user, overlaid with floating holographic particles.
- **Key Elements**:
  - Glitch-animated title text that shifts between Cyan and Magenta.
  - Three chamfered "HUD Cards" showcasing core features (Intelligent AI, Voice Synthesis, Visual Recognition).
  - A prominent "INITIALIZE SYSTEM" button triggering Sci-Fi UI sound effects.

### 2. Authentication Page (`SignInPage.vue`)
- **Aesthetic**: Continues the dark Cyberpunk grid theme. Features an animated pink neon border that traces around the central glassmorphism login card.
- **Functionality**:
  - Offers Google OAuth login (via `@react-oauth/google` structure) or Guest Mode.
  - A custom warning modal blocks unauthorized Guest access to cloud tools (Calendar, etc.) while allowing basic chat.

### 3. "Link Start" Transition Sequence
*When authentication succeeds, a custom multi-phase cinematic transition (`startLinkSequence`) takes over the screen before loading the main chat:*
- **Phase 1 (T+0s)**: "IDENTITY VERIFIED" badge appears with an audio confirmation.
- **Phase 2 (T+3s)**: "CONNECTING TO VIRTUAI COMPANION...". The flat 3D grid smoothly bends into a circular "Warp Tunnel" using linear interpolation and camera rotation.
- **Phase 3 (T+4.5s)**: "LINK START". The grid accelerates exponentially (fisheye warp effect), accompanied by a heavy whoosh sound. The floating particles stretch into a high-speed Matrix-style character rain (green Katakana/Numbers) rushing past the camera.
- **Phase 4 (T+6.5s)**: A white flash bursts and fills the screen, resolving the dive.
- **Phase 5 (T+9.5s)**: Router pushes the user into the main `/chat` interface.

### 4. Main Chat Interface (`CharacterView.vue` / `/chat`)
- **Layout**: A split-screen design.
  - **Left panel**: A translucent glass chat window logging user and AI messages.
  - **Right panel/Background**: The core `Three.js` scene rendering the rigged `.vrm` 3D character (Suzune).
- **Features**: 
  - Dynamic webcam HUD overlay in the corner running MediaPipe for emotion detection.
  - Microphone amplitude visualizers.
  - The character actively tracking the user and playing corresponding Mixamo FBX animations (`retargetClip` mapped) during conversation.

### 5. Desktop Pet Mode (`DesktopPetView.vue`)
- **Aesthetic**: A borderless, fully transparent window that floats above all other desktop applications. 
- **Interaction Flow**:
  - The VRM character autonomously walks across the user's actual Windows desktop, stops, looks around, or idles.
  - Built with an invisible 3D bounding box for high-performance click detection without raycasting lag.
  - **Soft Sync**: Includes a synchronized chat interface that ties back to the main web app's conversation threads.
  - Features a system tray integration / right-click context menu for easy exit.

### 6. Control Panel & Settings (`ModelSettings.vue`, `VoiceSettings.vue`)
- **Aesthetic**: Continuing the glassmorphism theme with dedicated dashboard layouts for admin-level controls.
- **Functionality**:
  - **Model Settings**: Allows developers to adjust 3D scene lighting, test FBX animation retargeting (e.g., forcing a wave or walk animation), and swap `.vrm` assets dynamically.
  - **Voice Settings**: Interface to upload new `.wav` ground-truth reference audio for the XTTS-v2 cloning engine, test TTS latency, and manage the cached audio library.

### 7. Telegram Bot Interface (`telegram_bot.py`)
- **Aesthetic**: Native Telegram UI, acting as a lightweight mobile/remote client.
- **Functionality**:
  - Connects to the exact same core `AIService` as the web application.
  - Supports `/start`, `/help`, and custom skill triggers (like `/youtube`).
  - Allows text and voice interaction while away from the desktop, ensuring the VirtuAI Companion is continuously accessible across devices.
