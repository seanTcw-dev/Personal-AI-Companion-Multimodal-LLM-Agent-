# 🎤 Voice Integration Setup Guide

## ✅ What's Been Added

Your Anime Model Chatbot now has **voice cloning** integrated! Suzune Horikita will speak all AI responses with her own voice.

### New Features:
- 🎤 **Automatic Voice Generation** - Every AI response is spoken
- 🗣️ **Character Voice** - Suzune Horikita's voice
- 🗑️ **Auto Cleanup** - Audio files deleted after 60 seconds
- 🌐 **Multi-language** - Supports English and Chinese

---

## 📁 Setup Instructions

### Step 1: Add Suzune's Voice Sample

**You need to add your Suzune Horikita MP3 file:**

```
backend/app/static/voices/suzune_horikita.mp3
```

**How to add it:**
1. Find your Suzune voice MP3 file
2. Rename it to: `suzune_horikita.mp3`
3. Copy it to: `backend/app/static/voices/`

**Voice Sample Requirements:**
- ✅ Clear audio (no background noise)
- ✅ 3-10 seconds long
- ✅ MP3, WAV, FLAC, or OGG format
- ✅ Single speaker only

---

### Step 2: Install Voice Dependencies

The voice cloning requires the TTS library (already in requirements.txt):

```powershell
# If not already installed
conda activate aniChatbot_final
pip install TTS==0.22.0
```

---

### Step 3: Restart Backend

```powershell
cd backend
python run.py
```

**You should see:**
```
🎤 Initializing Voice Cloning Service...
🔧 Using device: cuda  # or cpu
📥 Loading XTTS model...
✅ Voice Cloning Service initialized successfully!
🗑️ Audio cleanup thread started
```

---

## 🎯 How It Works

### Workflow:
1. **User sends message** → "What can you do?"
2. **Gemini generates text** → "I can help you with..."
3. **🎤 Voice auto-generates** → Creates audio with Suzune's voice
4. **Frontend receives:**
   ```json
   {
     "text": "I can help you with many things!",
     "emotion": "happy",
     "audio_url": "/api/voice/audio/voice_12345.wav"
   }
   ```
5. **Frontend plays audio** → Character speaks!
6. **Auto-cleanup** → File deleted after 60 seconds

### File Lifecycle:
```
Generate (0s) → Play (5s) → Wait (60s) → Delete ✅
```

---

## 🎭 Character Configuration

Currently configured:
- **Name:** Suzune Horikita
- **Voice File:** suzune_horikita.mp3
- **Default Language:** English (auto-detects Chinese)

### Adding More Characters (Future):

Edit `backend/app/services/voice_service.py`, line 27:

```python
self.characters = {
    "suzune_horikita": {
        "name": "Suzune Horikita",
        "voice_file": "suzune_horikita.mp3",
        "language": "en"
    },
    "new_character": {  # Add new character
        "name": "New Character",
        "voice_file": "new_character.mp3",
        "language": "en"
    }
}
```

---

## 🔧 Configuration

### Change Cleanup Time

Edit `voice_service.py`, line 35:
```python
self.cleanup_interval = 60  # Change to 120 for 2 minutes
```

### Change Language

The service auto-detects language, but you can force it:

Edit `websockets.py`, line 52:
```python
audio_url = await voice_service.generate_voice(
    text=ai_response['text'],
    character_name="suzune_horikita",
    language="zh-cn"  # Force Chinese
)
```

---

## 🐛 Troubleshooting

### Voice Not Playing

1. **Check backend console** for errors:
   ```
   🎤 Generating voice for response...
   ✅ Voice generated: /api/voice/audio/voice_xxxxx.wav
   ```

2. **Check if voice file exists:**
   ```powershell
   dir backend\app\static\voices\suzune_horikita.mp3
   ```

3. **Test voice service:**
   ```powershell
   cd backend
   python -c "from app.services.voice_service import voice_service; print('Voice service loaded!')"
   ```

### Model Loading Errors

**Error:** `Model not loaded`
- **Solution:** Check internet connection (first load downloads model)
- **Solution:** Ensure you have ~2GB free disk space

**Error:** `CUDA out of memory`
- **Solution:** Service will automatically fall back to CPU
- **Solution:** Close other programs to free up memory

### Audio File Not Found (404)

- **Check:** Backend is running
- **Check:** File hasn't been cleaned up yet (wait < 60s)
- **Check:** Audio generation didn't fail (check console)

---

## 🎮 Frontend Integration (Next Step)

The backend now sends `audio_url` in responses. You need to update the frontend to play the audio:

**In `ChatMessageList.vue` or similar:**
```javascript
// When receiving AI message
if (message.audio_url) {
  const audio = new Audio(message.audio_url);
  audio.play();
}
```

---

## 📊 API Endpoints

### Voice Audio Streaming
```
GET /api/voice/audio/{filename}
```

Returns: WAV audio file stream

**Example:**
```
http://localhost:8000/api/voice/audio/voice_abc123.wav
```

### Health Check
```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "ai_service": "gemini",
  "voice_service": "xtts",
  "character": "suzune_horikita"
}
```

---

## 🗂️ File Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── voice.py              ✅ NEW - Voice endpoints
│   │   └── websockets.py         ✅ Updated - Auto voice generation
│   ├── services/
│   │   ├── gemini_service.py     (existing)
│   │   └── voice_service.py      ✅ NEW - Voice cloning logic
│   ├── static/
│   │   ├── voices/               ✅ NEW - Put suzune_horikita.mp3 here
│   │   └── temp_audio/           ✅ NEW - Generated audio (auto-cleanup)
│   └── main.py                   ✅ Updated - Added voice routes
```

---

## 💡 Tips

1. **Voice Sample Quality Matters**
   - Use clear, high-quality audio
   - Remove background noise
   - 5-10 seconds is ideal

2. **First Generation is Slow**
   - Model downloads on first use (~1-2 minutes)
   - Subsequent generations are fast (~2-5 seconds)

3. **GPU Recommended**
   - CUDA GPU: ~2 seconds per response
   - CPU: ~10-15 seconds per response

4. **Storage Management**
   - Auto-cleanup keeps disk usage low
   - Each audio file ~200-500 KB
   - Max ~10 files at a time

---

## 🚀 Next Steps

1. ✅ Add `suzune_horikita.mp3` to `backend/app/static/voices/`
2. ✅ Restart backend server
3. ✅ Test by sending a message
4. 🔄 Update frontend to play audio (see Frontend Integration section)
5. 🎭 Add lip-sync animation (advanced)

---

**Happy Chatting with Voice! 🎉**
