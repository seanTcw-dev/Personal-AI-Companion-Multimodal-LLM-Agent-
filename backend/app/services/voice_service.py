"""
Voice Cloning Service
Handles text-to-speech with voice cloning using XTTS model
"""
import os
import uuid
import torch
import asyncio
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import threading
import time
import io
import wave
import numpy as np
import json
from fastapi import UploadFile

class VoiceService:
    def __init__(self):
        """Initialize the Voice Cloning service"""
        self.model = None  # Raw XTTS model
        self.device = None
        self.config = None  # XTTS config
        self.base_dir = Path(__file__).parent.parent
        self.voices_dir = self.base_dir / "static" / "voices"
        self.test_audio_dir = self.base_dir / "static" / "voices" / "testAudio"
        self.temp_audio_dir = self.base_dir / "static" / "temp_audio"
        self.cache_dir = self.base_dir / "static" / "voice_cache"
        self.latents_cache_dir = self.base_dir / "static" / "character_voice_cache"
        self.system_cache_dir = self.base_dir / "static" / "system_cache"
        self.profiles_path = self.base_dir / "static" / "profiles.json"
        
        # New: Persist active character selection
        self.settings_json_path = self.base_dir / "static" / "voice_settings.json"
        
        # Ensure directories exist
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.test_audio_dir.mkdir(parents=True, exist_ok=True)
        self.temp_audio_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.latents_cache_dir.mkdir(parents=True, exist_ok=True)
        self.system_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Character voice configurations with pre-computed embeddings
        self.characters = {
            "suzune_horikita": {
                "name": "Suzune Horikita",
                "voice_file": "suzune_horikita.mp3",
                "language": "en",
                "gpt_cond_latent": None,  # Will be computed on first use
                "speaker_embedding": None
            }
        }
        
        # Load custom profiles first
        self._load_profiles()
        
        # Track active custom character
        self.active_custom_character = None
        
        # Load persisted selection (if any)
        self._load_settings()
        
        # Track generated files for cleanup
        self.generated_files: Dict[str, datetime] = {}
        self.cleanup_interval = 60  # seconds
        
        # Cache mapping: text_hash -> audio filename
        self.audio_cache: Dict[str, str] = {}
        self.cache_enabled = True  # Enable caching
        self.use_streaming = False  # Disable streaming - standard mode is faster for short texts
        self.streaming_threshold = 1000  # Only use streaming for very long texts (1000+ chars)
        self.stream_chunk_size = 50  # Larger chunks for faster processing
        self.request_count = 0 # Counter for demo mode
        
        # Start cleanup thread
        self.start_cleanup_thread()
        
        print("🎤 Voice Service Initialized (Model Idle)")
        # self._load_model() # LAZY LOAD: Don't load on startup
        
    def preload_model_if_needed(self):
        """
        Preload model and embeddings if an active character is set.
        Call this from startup event to speed up first request.
        """
        if self.active_custom_character or True:  # Always preload for default character
            print("🚀 Preloading XTTS model and embeddings for faster first response...")
            try:
                # Load model synchronously (we're in startup, blocking is OK)
                self._load_model()
                
                # Preload embeddings for active character
                active_char = self.active_custom_character or "suzune_horikita"
                print(f"📦 Preloading embeddings for: {active_char}")
                self._get_conditioning_latents(active_char)
                
                print("✅ Model and embeddings preloaded successfully!")
            except Exception as e:
                print(f"⚠️ Failed to preload model: {e}")
                import traceback
                traceback.print_exc()

    async def _ensure_model_loaded(self):
        """Ensure XTTS model is loaded (called on Apply)"""
        if self.model:
            return

        print("🚀 Loading XTTS Model (Lazy Init)...")
        # Run synchronous load in thread to avoid blocking too much (though it's heavy)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)

    def _load_model(self):
        """Load the raw XTTS model for streaming support"""
        try:
            # Check if CUDA is available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🔧 Using device: {self.device}")
            
            # Import raw XTTS model and config
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.tts.models.xtts import Xtts
            from TTS.utils.generic_utils import get_user_data_dir
            from TTS.utils.manage import ModelManager
            
            # Set environment variable to bypass license prompt
            os.environ['COQUI_TOS_AGREED'] = "1"
            
            print("📥 Loading XTTS model (first time may take a few minutes)...")
            
            # Download model if needed
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            ModelManager().download_model(model_name)
            model_path = os.path.join(get_user_data_dir("tts"), model_name.replace("/", "--"))
            
            # Load config
            self.config = XttsConfig()
            self.config.load_json(os.path.join(model_path, "config.json"))
            
            # Load model
            self.model = Xtts.init_from_config(self.config)
            self.model.load_checkpoint(
                self.config, 
                checkpoint_dir=model_path, 
                eval=True,
                use_deepspeed=False  # Disable deepspeed for compatibility
            )
            self.model.to(self.device)
            
            # Enable GPU optimizations if using CUDA
            if self.device == "cuda":
                print("⚡ Enabling GPU optimizations...")
                # Use half precision (FP16) for faster inference on RTX GPUs
                # self.model = self.model.half()  # Commented: May cause issues with some ops
                # Enable cuDNN benchmarking for optimal performance
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.enabled = True
                print("✅ GPU optimizations enabled")
            
            print("✅ Voice Cloning Service initialized successfully!")
            print("🌊 Streaming support: ENABLED")
            
        except Exception as e:
            print(f"❌ Error loading XTTS model: {e}")
            print("Voice cloning will not be available.")
            import traceback
            traceback.print_exc()
            self.model = None

    def _load_settings(self):
        """Load persistent voice settings (active character ID)"""
        try:
            if self.settings_json_path.exists():
                with open(self.settings_json_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    saved_active = settings.get("active_character_id")
                    
                    if saved_active and saved_active in self.characters:
                        print(f"🔄 Restoring active character from settings: {saved_active}")
                        self.active_custom_character = saved_active
        except Exception as e:
            print(f"⚠️ Failed to load voice settings: {e}")

    def _save_voice_settings(self):
        """Save active character selection to JSON"""
        try:
            settings = {
                "active_character_id": self.active_custom_character
            }
            with open(self.settings_json_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            print("💾 Voice settings saved")
        except Exception as e:
            print(f"❌ Failed to save voice settings: {e}")

    def _load_profiles(self):
        """Load custom character profiles from JSON and recover missing files"""
        try:
            # 1. Load from JSON
            if self.profiles_path.exists():
                print(f"📂 Loading profiles from {self.profiles_path}")
                with open(self.profiles_path, "r", encoding="utf-8") as f:
                    saved_profiles = json.load(f)
                    for char_id, profile in saved_profiles.items():
                        # Restore into self.characters if not already present
                        if char_id not in self.characters:
                            self.characters[char_id] = {
                                "name": profile["name"],
                                "voice_file": profile["voice_file"],
                                "language": profile.get("language", "en"),
                                "gpt_cond_latent": None,
                                "speaker_embedding": None,
                                "is_test": False
                            }
            
            # 2. Auto-Recovery: DISABLED (User request)
            # We do NOT scan for orphan files anymore to prevents ghost characters.
            print("INFO: Auto-recovery of orphan voice files is DISABLED.")
                
        except Exception as e:
            print(f"❌ Error loading profiles: {e}")

    def _save_profiles(self):
        """Save custom character profiles to JSON"""
        try:
            profiles_to_save = {}
            for char_id, char_data in self.characters.items():
                # Skip default character and test characters
                if char_id == "suzune_horikita" or char_data.get("is_test", False):
                    continue
                
                profiles_to_save[char_id] = {
                    "name": char_data["name"],
                    "voice_file": char_data["voice_file"],
                    "language": char_data.get("language", "en")
                }
            
            with open(self.profiles_path, "w", encoding="utf-8") as f:
                json.dump(profiles_to_save, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Profiles saved to {self.profiles_path}")
            
        except Exception as e:
            print(f"❌ Error saving profiles: {e}")

    def get_character_voice_path(self, character_name: str) -> Optional[Path]:
        """Get the voice sample path for a character"""
        if character_name not in self.characters:
            print(f"⚠️ Character '{character_name}' not found")
            return None
        
        character = self.characters[character_name]
        voice_file = character["voice_file"]
        
        # Check if it's a test voice (in testAudio folder)
        if character.get("is_test", False):
            voice_path = self.test_audio_dir / voice_file
        else:
            voice_path = self.voices_dir / voice_file
        
        if not voice_path.exists():
            print(f"⚠️ Voice file not found: {voice_path}")
            return None
        
        return voice_path

    def _get_latents_cache_path(self, character_name: str) -> Path:
        """Get writable path for cached latents file"""
        # User requested: {name}_cache.pt in character_voice_cache folder
        return self.latents_cache_dir / f"{character_name}_cache.pt"

    def _find_existing_latents_path(self, character_name: str) -> Optional[Path]:
        """Find existing latents file (check user cache first, then system cache)"""
        # 1. Check User Cache (Writable)
        user_path = self.latents_cache_dir / f"{character_name}_cache.pt"
        if user_path.exists():
            return user_path
        
        # 2. Check System Cache (Read-Only / Pre-baked)
        system_path = self.system_cache_dir / f"{character_name}_cache.pt"
        if system_path.exists():
            return system_path
            
        return None

    def _get_conditioning_latents(self, character_name: str):
        """Get or compute conditioning latents for a character"""
        if not self.model:
            print("❌ Model not loaded")
            return None, None
            
        character = self.characters.get(character_name)
        if not character:
            return None, None
        
        # 1. Check Memory Cache
        if character["gpt_cond_latent"] is not None and character["speaker_embedding"] is not None:
            return character["gpt_cond_latent"], character["speaker_embedding"]
        
        # Get voice file path
        voice_path = self.get_character_voice_path(character_name)
        if not voice_path:
            return None, None
            
        # 2. Check Disk Cache (User & System)
        latents_path = self._find_existing_latents_path(character_name)
        if latents_path and latents_path.exists():
            try:
                print(f"💾 Loading cached voice embeddings from: {latents_path.name}")
                latents = torch.load(latents_path, map_location=self.device)
                
                gpt_cond_latent = latents["gpt_cond_latent"]
                speaker_embedding = latents["speaker_embedding"]
                
                # Update memory cache
                character["gpt_cond_latent"] = gpt_cond_latent
                character["speaker_embedding"] = speaker_embedding
                
                return gpt_cond_latent, speaker_embedding
            except Exception as e:
                print(f"⚠️ Failed to load cached latents (will recompute): {e}")

        # 3. Compute from voice file (Fallback)
        try:
            print(f"🎯 Computing voice embeddings for {character_name}...")
            start_time = time.time()
            
            gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(
                audio_path=str(voice_path)
            )
            
            # Cache in memory
            character["gpt_cond_latent"] = gpt_cond_latent
            character["speaker_embedding"] = speaker_embedding
            
            # 4. Save to Disk
            try:
                # If we didn't load from cache, we need to know where to save
                if not latents_path:
                    latents_path = self._get_latents_cache_path(character_name)
                    
                print(f"💾 Saving voice embeddings to disk: {latents_path}")
                torch.save({
                    "gpt_cond_latent": gpt_cond_latent,
                    "speaker_embedding": speaker_embedding
                }, latents_path)
            except Exception as e:
                print(f"⚠️ Failed to save latents to disk: {e}")
            
            duration = time.time() - start_time
            print(f"✅ Voice embeddings computed in {duration:.2f}s")
            return gpt_cond_latent, speaker_embedding
            
        except Exception as e:
            print(f"❌ Error computing voice embeddings: {e}")
            return None, None

    def _clean_text_for_speech(self, text: str) -> str:
        """Remove emojis and other non-speakable characters from text"""
        import re
        
        # Remove emojis (comprehensive pattern)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U00002600-\U000026FF"  # misc symbols
            "]+", 
            flags=re.UNICODE
        )
        
        # Remove emojis
        cleaned = emoji_pattern.sub('', text)
        
        # Replace special punctuation/symbols that TTS might read literally
        # These will be replaced with pauses (commas) or removed
        replacements = {
            '*': '',        # Remove asterisks (markdown bold/italic)
            '_': '',        # Remove underscores
            '~': '',        # Remove tildes
            '`': '',        # Remove backticks
            '|': ',',       # Replace pipe with comma (pause)
            '—': ',',       # Replace em dash with comma
            '–': ',',       # Replace en dash with comma
            '...': '.',     # Replace ellipsis with period
            '…': '.',       # Replace unicode ellipsis
            '"': '',        # Remove quotes
            '"': '',
            '"': '',
            ''': '',
            ''': '',
            '「': '',       # Remove Japanese quotes
            '」': '',
            '【': '',       # Remove Chinese brackets
            '】': '',
            '《': '',
            '》': '',
            '·': '',        # Remove middle dot
            '•': ',',       # Replace bullet with comma
            '→': ',',       # Replace arrow with comma
            '←': ',',
            '↑': ',',
            '↓': ',',
            '♪': '',        # Remove music notes
            '♫': '',
            '♬': '',
            '♭': '',
            '♯': '',
            '°': ' degrees ', # Replace degree symbol
            '±': ' plus minus ',
            '×': ' times ',
            '÷': ' divided by ',
            '%': ' percent',
            '&': ' and ',
            '@': ' at ',
            '#': ' number ',
            '$': ' dollars ',
            '€': ' euros ',
            '£': ' pounds ',
            '¥': ' yen ',
            '©': '',        # Remove copyright
            '®': '',        # Remove registered
            '™': '',        # Remove trademark
            '[]': '',       # Remove brackets
            '()': '',       # Remove parentheses
            '{}': '',       # Remove braces
            '<>': '',       # Remove angle brackets
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove multiple punctuation marks (e.g., "!!!" -> "!")
        cleaned = re.sub(r'([!?.]){2,}', r'\1', cleaned)
        
        # Remove excessive commas
        cleaned = re.sub(r',{2,}', ',', cleaned)
        
        # Remove extra spaces created by replacements
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove leading/trailing punctuation except sentence-ending ones
        cleaned = re.sub(r'^[,;:\-]+', '', cleaned)
        cleaned = re.sub(r'[,;:\-]+$', '', cleaned)
        
        return cleaned

    async def generate_voice(
        self, 
        text: str, 
        character_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate voice audio from text using character's voice
        
        Args:
            text: Text to synthesize
            character_name: Character to use for voice cloning (use active character if None)
            language: Language code (en, zh-cn, etc.) - auto-detect if None
            
        Returns:
            Relative URL path to generated audio file, or None if failed
        """
        # Lazy Loading Logic:
        # 1. If active character is set (e.g. from previous session), AUTO-LOAD model.
        # 2. If no active character (fresh start), DO NOT load model (Silent Mode).
        if not self.model:
            target_char = character_name or self.active_custom_character
            
            if target_char:
                print(f"🔄 Auto-loading model for active character: {target_char}")
                # We can't await here directly if called from sync context, but this method IS async
                # Wait.. generate_voice is async def. OK.
                # However, this method calls _generate_audio_sync in run_in_executor.
                # The model must be loaded BEFORE likely.
                # But _ensure_model_loaded is async.
                
                # We need to AWAIT ensure_model_loaded here.
                # But we are inside generate_voice which is async. So we can await.
                await self._ensure_model_loaded()
            else:
                print("ℹ️ Voice model not loaded & no active voice. Skipping audio.")
                return None
        
        # Use active character if none specified
        if character_name is None:
            character_name = self.get_active_character()
            print(f"🎭 Using active character: {character_name}")
        
        if not text or not text.strip():
            print("❌ Empty text provided")
            return None
        
        try:
            # Clean text: remove emojis and non-speakable characters
            cleaned_text = self._clean_text_for_speech(text)
            
            if not cleaned_text or not cleaned_text.strip():
                print("⚠️ Text is empty after cleaning (only emojis?)")
                return None
            
            # Use cleaned text for TTS, but original text for cache key
            # (so "Hello 😊" and "Hello 😄" are treated as different)
            
            # Detect language if not provided
            if not language:
                language = self._detect_language(cleaned_text)
            
            # Create cache key from ORIGINAL text + character + language
            cache_key = hashlib.md5(
                f"{text}_{character_name}_{language}".encode()
            ).hexdigest()
            
            # Check cache first (fastest option)
            if self.cache_enabled and cache_key in self.audio_cache:
                cached_filename = self.audio_cache[cache_key]
                cached_path = self.cache_dir / cached_filename
                
                if cached_path.exists():
                    print(f"💾 Using cached audio for: {cleaned_text[:50]}...")
                    # Update access time to prevent deletion
                    self.generated_files[str(cached_path)] = datetime.now()
                    return f"/api/voice/audio/{cached_filename}"
                else:
                    # Cache entry exists but file deleted, remove from cache
                    del self.audio_cache[cache_key]
            
            # Decide: Use streaming or regular generation?
            use_streaming_for_this = self.use_streaming and len(cleaned_text) > self.streaming_threshold
            
            # Generate unique filename
            filename = f"voice_{uuid.uuid4().hex}.wav"
            output_path = self.cache_dir / filename  # Save to cache directory
            
            if use_streaming_for_this:
                print(f"🌊 Generating voice with STREAMING for: {cleaned_text[:50]}...")
            else:
                print(f"🎤 Generating voice for: {cleaned_text[:50]}...")
            
            print(f"   Character: {character_name}")
            print(f"   Language: {language}")
            print(f"   Method: {'Streaming' if use_streaming_for_this else 'Standard'}")
            
            # Run TTS in a thread to avoid blocking
            # Use CLEANED text for speech generation
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._generate_audio_sync,
                cleaned_text,  # Use cleaned text!
                character_name,  # Pass character name instead of voice_path
                language,
                str(output_path),
                use_streaming_for_this  # Pass streaming decision
            )
            
            # Add to cache
            if self.cache_enabled:
                self.audio_cache[cache_key] = filename
                print(f"💾 Cached audio with key: {cache_key[:8]}...")
            
            # Track file for cleanup
            self.generated_files[str(output_path)] = datetime.now()
            
            print(f"✅ Voice generated: {filename}")
            
            # Return relative URL path
            return f"/api/voice/audio/{filename}"
            
        except Exception as e:
            print(f"❌ Error generating voice: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_audio_sync(self, text: str, character_name: str, language: str, output_path: str, use_streaming: bool = False):
        """Synchronous audio generation (runs in thread)"""
        # Use torch.no_grad() for faster inference (no gradient computation)
        with torch.no_grad():
            try:
                if not self.model:
                    raise Exception("Model not loaded")
                    
                # Get conditioning latents
                gpt_cond_latent, speaker_embedding = self._get_conditioning_latents(character_name)
                
                if gpt_cond_latent is None or speaker_embedding is None:
                    raise Exception("Failed to get voice embeddings")
                
                if use_streaming:
                    # Use streaming generation (inference_stream)
                    print("🌊 Using TRUE streaming generation...")
                    try:
                        chunks = list(self.model.inference_stream(
                            text,
                            language,
                            gpt_cond_latent,
                            speaker_embedding,
                            stream_chunk_size=self.stream_chunk_size,
                            enable_text_splitting=True
                        ))
                        
                        print(f"📦 Received {len(chunks)} chunks from streaming")
                        
                        # Check if we got any chunks
                        if not chunks:
                            print("⚠️ No chunks received from streaming, falling back to standard mode")
                            raise Exception("Empty chunks from streaming")
                        
                        # Concatenate all chunks
                        if isinstance(chunks[0], list):
                            wav = torch.cat(chunks, dim=0)
                        else:
                            wav = torch.cat([c for c in chunks], dim=0)
                        
                        print(f"✅ Successfully concatenated {len(chunks)} chunks")
                        
                    except Exception as stream_error:
                        print(f"⚠️ Streaming failed: {stream_error}, falling back to standard mode")
                        # Fallback to standard generation
                        out = self.model.inference(
                            text,
                            language,
                            gpt_cond_latent,
                            speaker_embedding,
                            temperature=0.65,
                            length_penalty=1.0,
                            repetition_penalty=5.0,
                            top_k=50,
                            top_p=0.85
                        )
                        wav = torch.tensor(out["wav"])
                    
                else:
                    # Use standard generation (inference)
                    print("🎤 Using standard generation...")
                    out = self.model.inference(
                        text,
                        language,
                        gpt_cond_latent,
                        speaker_embedding,
                        temperature=0.65,  # Lower = faster, less variation (default 0.85)
                        length_penalty=1.0,
                        repetition_penalty=5.0,  # Prevent repetition
                        top_k=50,
                        top_p=0.85
                    )
                    wav = torch.tensor(out["wav"])
                
                # Post-process and save
                wav = wav.clone().detach().cpu().numpy()
                wav = wav[None, : int(wav.shape[0])]
                wav = np.clip(wav, -1, 1)
                wav = (wav * 32767).astype(np.int16)
                
                # Save as WAV file
                with wave.open(output_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)  # XTTS sample rate
                    wav_file.writeframes(wav.tobytes())
                    
            except Exception as e:
                print(f"❌ Error in TTS generation: {e}")
                import traceback
                traceback.print_exc()
                raise

    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        import re
        
        # Count Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # Count English letters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = chinese_chars + english_chars
        
        if total_chars == 0:
            return "en"
        
        # If more than 30% Chinese, use Chinese
        if chinese_chars / total_chars > 0.3:
            return "zh-cn"
        
        return "en"

    def start_cleanup_thread(self):
        """Start background thread to cleanup old audio files"""
        def cleanup_loop():
            while True:
                time.sleep(self.cleanup_interval)
                self.cleanup_old_files()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        print("🗑️ Audio cleanup thread started")

    def cleanup_old_files(self):
        """Delete old audio files, but keep cached files"""
        try:
            current_time = datetime.now()
            files_to_delete = []
            
            for file_path, created_time in list(self.generated_files.items()):
                file_path_obj = Path(file_path)
                
                # Check if file is in cache directory
                is_cached = str(self.cache_dir) in str(file_path_obj.parent)
                
                if is_cached:
                    # Cached files: Delete after 24 hours (keep longer for reuse)
                    max_age = timedelta(hours=24)
                else:
                    # Temp files: Delete after 60 seconds
                    max_age = timedelta(seconds=60)
                
                # Delete files older than max_age
                if current_time - created_time > max_age:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            if is_cached:
                                print(f"🗑️ Cleaned up cached file (24h old): {os.path.basename(file_path)}")
                                # Also remove from cache dictionary
                                cache_keys_to_delete = [k for k, v in self.audio_cache.items() if v == file_path_obj.name]
                                for key in cache_keys_to_delete:
                                    del self.audio_cache[key]
                            else:
                                print(f"🗑️ Cleaned up temp file: {os.path.basename(file_path)}")
                        files_to_delete.append(file_path)
                    except Exception as e:
                        print(f"⚠️ Could not delete {file_path}: {e}")
            
            # Remove from tracking
            for file_path in files_to_delete:
                self.generated_files.pop(file_path, None)
                
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

    def get_audio_file_path(self, filename: str) -> Optional[Path]:
        """Get the full path to an audio file (check both cache and temp)"""
        # Check cache directory first
        cache_path = self.cache_dir / filename
        if cache_path.exists():
            return cache_path
        
        # Check temp directory
        temp_path = self.temp_audio_dir / filename
        if temp_path.exists():
            return temp_path
        
        return None

    async def save_custom_voice(self, file: UploadFile) -> str:
        """
        Save uploaded custom voice file to test directory (temporary)
        
        Args:
            file: Uploaded audio file
            
        Returns:
            Character ID for the custom voice
        """
        try:
            # Validate filename
            if not file.filename:
                raise ValueError("Filename is required")
            
            # Generate unique character ID
            character_id = f"test_{uuid.uuid4().hex[:8]}"
            
            # Get file extension
            file_ext = "." + file.filename.split(".")[-1].lower()
            voice_filename = f"{character_id}{file_ext}"
            voice_path = self.test_audio_dir / voice_filename  # Save to testAudio first
            
            # Save the uploaded file
            print(f"💾 Saving test voice to: {voice_path}")
            with open(voice_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Add to characters dictionary (temporary status)
            self.characters[character_id] = {
                "name": f"Test Voice ({file.filename})",
                "voice_file": voice_filename,
                "language": "en",  # Default, will auto-detect
                "gpt_cond_latent": None,
                "speaker_embedding": None,
                "is_test": True,  # Mark as test voice
                "original_filename": file.filename
            }
            
            print(f"✅ Test voice saved: {character_id}")
            return character_id
            
        except Exception as e:
            print(f"❌ Error saving test voice: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def set_active_custom_voice(self, character_id: str) -> bool:
        """
        Set a custom voice as the active voice for conversations
        AND ensure embeddings are computed/cached immediately.
        
        Args:
            character_id: ID of the custom character
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if character_id not in self.characters:
                print(f"⚠️ Character {character_id} not found")
                return False
            
            print(f"🔄 Activating voice: {character_id} (Checking cache...)")
            
            # 1. Ensure Model is Loaded (Lazy Init)
            await self._ensure_model_loaded()
            
            # Force generation/loading of latents NOW
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._get_conditioning_latents,
                character_id
            )
            
            # Set as active custom character
            self.active_custom_character = character_id
            
            # Save this selection to disk
            self._save_settings()
            
            character = self.characters[character_id]
            print(f"✅ Active voice set to: {character_id} ({character['name']})")
            return True
            
        except Exception as e:
            print(f"❌ Error setting active voice: {e}")
            return False

    async def finalize_custom_voice(self, character_id: str, custom_name: str) -> str:
        """
        Move test voice to permanent location with custom name
        
        Args:
            character_id: ID of the test character
            custom_name: User-provided name for the voice
            
        Returns:
            New permanent character ID
        """
        try:
            if character_id not in self.characters:
                raise ValueError(f"Character {character_id} not found")
            
            character = self.characters[character_id]
            if not character.get("is_test", False):
                raise ValueError("Character is not a test voice")
            
            # Sanitize custom name for ID and filename
            import re
            safe_name = re.sub(r'[^\w\-_]', '_', custom_name).lower()  # Lowercase, replace non-alphanumeric with _
            safe_name = re.sub(r'_{2,}', '_', safe_name)      # Collapse multiple _
            safe_name = safe_name.strip('_')
            
            if not safe_name:
                safe_name = f"voice_{uuid.uuid4().hex[:8]}"
            
            # Generate new permanent ID based on name
            permanent_id = f"custom_{safe_name}"
            
            # Handle collision for ID (append counter if ID exists)
            counter = 1
            base_id = permanent_id
            while permanent_id in self.characters:
                permanent_id = f"{base_id}_{counter}"
                counter += 1
            
            # Get original file extension
            old_path = self.test_audio_dir / character["voice_file"]
            file_ext = "." + character["voice_file"].split(".")[-1]
            
            # Create new filename (use permanent_id to match ID)
            new_filename = f"{permanent_id}{file_ext}"
            new_path = self.voices_dir / new_filename
            
            # Move file from testAudio to voices
            print(f"📦 Moving voice file: {old_path} → {new_path}")
            shutil.move(str(old_path), str(new_path))

            # ALSO Move/Rename the cache file if it exists
            # The cache file is named {id}_cache.pt
            old_cache_path = self.latents_cache_dir / f"{character_id}_cache.pt"
            new_cache_path = self.latents_cache_dir / f"{permanent_id}_cache.pt"
            
            if old_cache_path.exists():
                print(f"📦 Renaming cache file: {old_cache_path.name} → {new_cache_path.name}")
                shutil.move(str(old_cache_path), str(new_cache_path))
            else:
                print(f"⚠️ Cache file not found for {character_id}, skipping cache rename.")
            
            # Create permanent character entry
            self.characters[permanent_id] = {
                "name": custom_name,
                "voice_file": new_filename,
                "language": character["language"],
                "gpt_cond_latent": character["gpt_cond_latent"],  # Keep embeddings if computed
                "speaker_embedding": character["speaker_embedding"],
                "is_test": False
            }
            
            # Remove temporary character
            del self.characters[character_id]
            
            # Update active character if it was the test one
            if self.active_custom_character == character_id:
                self.active_custom_character = permanent_id
            
            print(f"✅ Voice finalized: {permanent_id} - '{custom_name}' (File: {new_filename})")
            
            # Save profiles to disk
            self._save_profiles()
            
            return permanent_id
            
        except Exception as e:
            print(f"❌ Error finalizing voice: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def delete_custom_character(self, character_id: str) -> bool:
        """
        Delete a custom character and its associated files
        
        Args:
            character_id: ID of the character to delete
            
        Returns:
            True if deleted successfully
        """
        # 1. Validation
        if not character_id.startswith("custom_"):
            print(f"❌ Cannot delete system character: {character_id}")
            return False
            
        try:
            # 2. Revert active character if needed
            if self.active_custom_character == character_id:
                print(f"⚠️ Deleting active character, reverting to default.")
                self.active_custom_character = None
                self._save_voice_settings()
                
            # 3. Delete Cache File (The most important part for the user)
            cache_path = self.latents_cache_dir / f"{character_id}_cache.pt"
            if cache_path.exists():
                print(f"🗑️ Deleting cache file: {cache_path}")
                cache_path.unlink()
            else:
                print(f"⚠️ Cache file not found: {cache_path}")
                
            # 4. Delete Audio File (Cleanup source)
            # Find the file in voices directory
            # We need to find the filename from self.characters OR guess it
            character = self.characters.get(character_id)
            if character:
                voice_filename = character.get("voice_file")
                if voice_filename:
                    audio_path = self.voices_dir / voice_filename
                    if audio_path.exists():
                        print(f"🗑️ Deleting audio file: {audio_path}")
                        audio_path.unlink()
                        
                # 5. Remove from Memory
                del self.characters[character_id]
                
                # 6. Save Profiles (Persist removal)
                self._save_profiles()
            else:
                 # If character not in memory (Ghost?), allow deleting cache anyway
                 pass

            print(f"✅ Character {character_id} deleted successfully.")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting character {character_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_active_character(self) -> str:
        """Get the currently active character ID"""
        return self.active_custom_character or "suzune_horikita"

    def get_available_characters(self) -> list:
        """
        Get list of all available characters THAT HAVE A CACHE FILE
        (User requested: Only show character_voice_cache names)
        
        Returns:
            List of character details
        """
        characters = []
        
        # 1. Scan System Cache (These are ALWAYS Default/System)
        system_ids = set()
        if self.system_cache_dir.exists():
            files = list(self.system_cache_dir.glob("*_cache.pt"))
            print(f"🔍 DEBUG: Found {len(files)} system cache files")
            for cache_file in files:
                char_id = cache_file.name.replace("_cache.pt", "")
                system_ids.add(char_id)

        # 2. Scan User Cache (These are Custom, unless overridden by System)
        user_ids = set()
        if self.latents_cache_dir.exists():
            files = list(self.latents_cache_dir.glob("*_cache.pt"))
            # print(f"🔍 DEBUG: Found {len(files)} user cache files")
            for cache_file in files:
                char_id = cache_file.name.replace("_cache.pt", "")
                user_ids.add(char_id)
            
        print(f"🔍 DEBUG: Active Character: {self.get_active_character()}")
        
        # 3. Combine and Filter
        all_ids = system_ids.union(user_ids)
        
        # Iterate over KNOWN characters (from profiles + default) OR all found IDs?
        # If a file exists but no profile, we should probably still show it?
        # But for now, let's stick to self.characters iteration to get NAMES correctly.
        
        # Wait, if user manually dropped a file, self.characters might not know its name.
        # But let's assume valid workflow for now.
        
        for char_id, char_data in self.characters.items():
            # Skip test characters
            if char_data.get("is_test", False):
                continue
            
            # Check availability
            in_system = char_id in system_ids
            in_user = char_id in user_ids
            
            # STRICT MODE: Must be cached in either
            if in_system or in_user:
                # Logic: If it's in system_cache, treat as Default System voice
                # Even if ID says "custom_", if it's in system folder, it's protected.
                is_system_override = in_system
                
                # Determine "is_custom" flag for Frontend (controls Badge & Delete button)
                # If cached in system -> Default (is_custom=False)
                # If cached in user AND NOT system -> Custom (is_custom=True)
                # (Note: char_id string might start with "custom_", but we override based on LOCATION)
                
                final_is_custom = False if is_system_override else char_id.startswith("custom_")
                
                is_active = char_id == self.get_active_character()
                
                print(f"✅ DEBUG: Including {char_id} (System: {in_system}, User: {in_user}) -> Custom: {final_is_custom}")
                
                characters.append({
                    "id": char_id,
                    "name": char_data["name"],
                    "is_custom": final_is_custom,  # Controls "Default" vs "Custom" badge
                    "is_active": is_active,
                    "is_system": is_system_override # Extra flag if needed
                })

        return characters
        
        return characters

# Create singleton instance
voice_service = VoiceService()
