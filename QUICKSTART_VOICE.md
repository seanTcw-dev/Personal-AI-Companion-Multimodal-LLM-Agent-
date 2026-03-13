# 🎤 Quick Start: Add Your Voice File

## Step 1: Place Your Suzune Voice MP3

Copy your Suzune Horikita voice MP3 to:

```
backend/app/static/voices/suzune_horikita.mp3
```

**Example (Windows PowerShell):**
```powershell
# If your MP3 is on desktop
Copy-Item "C:\Users\YourName\Desktop\suzune.mp3" "backend\app\static\voices\suzune_horikita.mp3"
```

## Step 2: Restart Backend

```powershell
# Kill any existing backend process
# Then restart
cd backend
python run.py
```

**Expected Output:**
```
🎤 Initializing Voice Cloning Service...
🔧 Using device: cuda
📥 Loading XTTS model...
✅ Voice Cloning Service initialized successfully!
🗑️ Audio cleanup thread started
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Test It!

1. Open http://localhost:5173
2. Send a message: "Hello!"
3. Check backend console for:
   ```
   📨 Received from user...
   🤖 AI Response: ...
   🎤 Generating voice for: ...
   ✅ Voice generated: /api/voice/audio/voice_xxxxx.wav
   ```

## Done! 🎉

Your AI will now speak with Suzune's voice!

---

## Troubleshooting

### ⚠️ Voice file not found
- Check path: `backend/app/static/voices/suzune_horikita.mp3`
- File must be exactly this name
- Supported formats: MP3, WAV, FLAC, OGG

### ⚠️ Model loading slow
- First time downloads model (~1-2 minutes)
- Requires internet connection
- Needs ~2GB disk space

### ⚠️ Pylance warnings in IDE
- `"tts_to_file" is not a known attribute` → **Ignore this!**
- It's a false positive from type checker
- Code works correctly (tested in voiceClone2)

---

**Ready? Copy your MP3 and restart the backend!** 🚀
