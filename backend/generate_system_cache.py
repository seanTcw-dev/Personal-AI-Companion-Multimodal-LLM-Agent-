
import os
import sys
import torch
import torch.nn as nn
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Setup paths
BASE_DIR = Path(r"c:\Users\SeanTeng\Desktop\Anime Model Chatbot\backend")
SYSTEM_CACHE_DIR = BASE_DIR / "app/static/system_cache"
VOICES_DIR = BASE_DIR / "app/static/voices"
MODEL_DIR = Path(r"C:\Users\SeanTeng\.cache\lm_studio\models\xtts")  # Approximate path, checking default
# If not default, try to find it or ask user?
# Wait, I can use VoiceService logic to load model.

sys.path.append(str(BASE_DIR))
from app.services.voice_service import VoiceService

def generate_system_cache():
    print("🚀 Initializing Voice Service (to load model)...")
    service = VoiceService()
    
    # Manually trigger model load
    print("⏳ Loading XTTS Model...")
    service._load_model()
    
    # Target character
    char_name = "suzune_horikita"
    mp3_path = VOICES_DIR / "suzune_horikita.mp3"
    target_cache_path = SYSTEM_CACHE_DIR / "suzune_horikita_cache.pt"
    
    if not mp3_path.exists():
        print(f"❌ Error: Source file not found: {mp3_path}")
        return
    
    print(f"🎤 Computing latents for {char_name} from {mp3_path.name}...")
    
    try:
        # Compute latents
        gpt_cond_latent, speaker_embedding = service.model.get_conditioning_latents(
            audio_path=[str(mp3_path)],
            gpt_cond_len=service.model.config.gpt_cond_len,
            max_ref_len=service.model.config.max_ref_len,
            sound_norm_refs=service.model.config.sound_norm_refs,
        )
        
        # Save to cache
        print(f"💾 Saving to System Cache: {target_cache_path}")
        torch.save({
            "gpt_cond_latent": gpt_cond_latent,
            "speaker_embedding": speaker_embedding,
        }, target_cache_path)
        
        print("✅ Success! Suzune is now pre-baked.")
        
    except Exception as e:
        print(f"❌ Error computing latents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_system_cache()
