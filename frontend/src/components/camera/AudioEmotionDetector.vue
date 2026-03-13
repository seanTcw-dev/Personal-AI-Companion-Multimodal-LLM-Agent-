<template>
  <div class="audio-detector">
    <!-- Audio visualization -->
    <div class="audio-controls">
      <button 
        class="audio-toggle-btn" 
        @click="toggleAudio"
        :class="{ active: audioActive }"
        :disabled="isLoading"
      >
        <svg v-if="!audioActive" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="1" y1="1" x2="23" y2="23"></line>
          <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
          <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
        {{ audioActive ? 'Mic: ON' : 'Mic: OFF' }}
      </button>
      
      <!-- Volume indicator -->
      <div class="volume-indicator" v-show="audioActive">
        <div class="volume-bar" :style="{ width: volumeLevel + '%' }"></div>
      </div>
      
      <!-- Detected sound badge -->
      <div class="sound-badge" v-show="audioActive && detectedSound">
        <span class="sound-icon">🔊</span>
        <span class="sound-text">{{ detectedSound }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, onMounted, defineEmits } from 'vue';

const emit = defineEmits(['emotionDetected', 'volumeLevel']);

const audioActive = ref(false);
const isLoading = ref(false);
const volumeLevel = ref(0);
const detectedSound = ref('');

let audioContext = null;
let analyser = null;
let microphone = null;
let javascriptNode = null;
let recognition = null;
let volumeCheckInterval = null;

// Cooldown management
let lastEmotionTime = 0;
let lastTranscript = '';
let isAISpeaking = false;
const DETECTION_COOLDOWN = 5000; // 5 seconds cooldown between detections

// Emotion sound patterns
const emotionSounds = {
  // Laughter patterns
  laughter: {
    patterns: ['haha', 'hehe', 'lol', 'laughing', 'giggle', 'chuckle'],
    emotion: 'Happy',
    confidence: 0.9
  },
  
  // Surprise sounds
  surprise: {
    patterns: ['wow', 'woah', 'oh my', 'omg', 'what', 'seriously', 'no way', 'gasp'],
    emotion: 'Surprised',
    confidence: 0.85
  },
  
  // Sad/crying sounds
  sadness: {
    patterns: ['sob', 'cry', 'sniff', 'sigh', 'oh no', 'damn', 'ugh'],
    emotion: 'Sad',
    confidence: 0.8
  },
  
  // Anger/frustration sounds
  anger: {
    patterns: ['argh', 'grrr', 'angry', 'mad', 'annoyed', 'seriously', 'what the'],
    emotion: 'Angry',
    confidence: 0.8
  },
  
  // Excitement sounds
  excitement: {
    patterns: ['yeah', 'yes', 'yay', 'awesome', 'amazing', 'great', 'woohoo'],
    emotion: 'Happy',
    confidence: 0.85
  }
};

// Toggle audio detection
const toggleAudio = async () => {
  if (audioActive.value) {
    stopAudio();
  } else {
    await startAudio();
  }
};

// Start audio detection
const startAudio = async () => {
  try {
    isLoading.value = true;
    
    // Request microphone access
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // Setup Web Audio API for volume detection
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    microphone = audioContext.createMediaStreamSource(stream);
    javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);
    
    analyser.smoothingTimeConstant = 0.8;
    analyser.fftSize = 1024;
    
    microphone.connect(analyser);
    analyser.connect(javascriptNode);
    javascriptNode.connect(audioContext.destination);
    
    // Monitor volume levels
    javascriptNode.onaudioprocess = () => {
      const array = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(array);
      const average = array.reduce((a, b) => a + b) / array.length;
      volumeLevel.value = Math.min((average / 128) * 100, 100);
      
      // Detect loud sounds (potential emotional outbursts)
      if (volumeLevel.value > 60) {
        detectLoudSound();
      }
      
      // Emit volume level for parent to use (e.g. for speaking detection)
      emit('volumeLevel', volumeLevel.value);
    };
    
    // Setup speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onresult = (event) => {
        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript.toLowerCase();
        const isFinal = event.results[last].isFinal;
        
        // Skip if AI is speaking
        if (isAISpeaking) {
          console.log('🤖 AI is speaking, skipping detection');
          return;
        }
        
        // Skip duplicate transcripts
        if (transcript === lastTranscript) {
          return;
        }
        
        // Only process final results or significantly different interim results
        if (isFinal || transcript.length > lastTranscript.length + 3) {
          console.log('🎤 Heard:', transcript);
          lastTranscript = transcript;
          analyzeAudioForEmotion(transcript);
        }
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
      };
      
      recognition.start();
      console.log('🎤 Speech recognition started');
    }
    
    audioActive.value = true;
    isLoading.value = false;
    console.log('✅ Audio emotion detection started');
    
  } catch (error) {
    console.error('❌ Error accessing microphone:', error);
    alert('Could not access microphone. Please check permissions.');
    isLoading.value = false;
  }
};

// Stop audio detection
const stopAudio = () => {
  if (recognition) {
    recognition.stop();
    recognition = null;
  }
  
  if (javascriptNode) {
    javascriptNode.disconnect();
    javascriptNode = null;
  }
  
  if (analyser) {
    analyser.disconnect();
    analyser = null;
  }
  
  if (microphone) {
    microphone.disconnect();
    microphone = null;
  }
  
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  
  if (volumeCheckInterval) {
    clearInterval(volumeCheckInterval);
    volumeCheckInterval = null;
  }
  
  audioActive.value = false;
  volumeLevel.value = 0;
  detectedSound.value = '';
  
  console.log('🛑 Audio detection stopped');
};

// Analyze audio for emotional content
const analyzeAudioForEmotion = (transcript) => {
  const now = Date.now();
  
  // Check cooldown
  if (now - lastEmotionTime < DETECTION_COOLDOWN) {
    const remainingCooldown = Math.ceil((DETECTION_COOLDOWN - (now - lastEmotionTime)) / 1000);
    console.log(`⏳ Cooldown active: ${remainingCooldown}s remaining`);
    return;
  }
  
  for (const [soundType, data] of Object.entries(emotionSounds)) {
    for (const pattern of data.patterns) {
      if (transcript.includes(pattern)) {
        console.log(`🔊 Detected ${soundType}: "${pattern}" → ${data.emotion}`);
        
        detectedSound.value = soundType.toUpperCase();
        lastEmotionTime = now;
        
        // Emit emotion to parent component
        emit('emotionDetected', {
          emotion: data.emotion,
          source: 'audio',
          sound: pattern,
          confidence: data.confidence,
          transcript: transcript
        });
        
        // Clear after 2 seconds
        setTimeout(() => {
          detectedSound.value = '';
        }, 2000);
        
        return;
      }
    }
  }
};

// Detect loud sounds (screams, gasps, etc.)
let lastLoudSoundTime = 0;
const detectLoudSound = () => {
  const now = Date.now();
  
  // Skip if AI is speaking or in cooldown
  if (isAISpeaking || now - lastEmotionTime < DETECTION_COOLDOWN) {
    return;
  }
  
  if (now - lastLoudSoundTime < 3000) return; // Debounce loud sounds
  
  lastLoudSoundTime = now;
  lastEmotionTime = now;
  
  console.log('📢 Loud sound detected!');
  detectedSound.value = 'LOUD SOUND';
  
  // Could indicate surprise or excitement
  emit('emotionDetected', {
    emotion: 'Surprised',
    source: 'audio',
    sound: 'loud_volume',
    confidence: 0.6,
    transcript: '[loud sound]'
  });
  
  setTimeout(() => {
    if (detectedSound.value === 'LOUD SOUND') {
      detectedSound.value = '';
    }
  }, 1500);
};

// Handle AI speaking state changes
const handleAISpeaking = (event) => {
  isAISpeaking = event.detail.speaking;
  if (isAISpeaking) {
    console.log('🤐 Pausing emotion detection - AI is speaking');
    // Reset transcript to avoid detecting AI speech
    lastTranscript = '';
  } else {
    console.log('👂 Resuming emotion detection - AI finished speaking');
  }
};

// Setup event listeners
onMounted(() => {
  window.addEventListener('ai-speaking', handleAISpeaking);
  console.log('🎧 Audio emotion detector mounted and listening');
});

// Cleanup on component unmount
onBeforeUnmount(() => {
  stopAudio();
  window.removeEventListener('ai-speaking', handleAISpeaking);
});
</script>

<style scoped>
.audio-detector {
  margin-top: 12px;
}

.audio-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.audio-toggle-btn {
  background: rgba(123, 45, 255, 0.2);
  border: 1px solid rgba(123, 45, 255, 0.5);
  color: var(--color-accent-tertiary);
  padding: 10px 16px;
  font-family: var(--font-display);
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  clip-path: polygon(
    8px 0,
    100% 0,
    100% calc(100% - 8px),
    calc(100% - 8px) 100%,
    0 100%,
    0 8px
  );
  backdrop-filter: blur(10px);
}

.audio-toggle-btn.active {
  background: rgba(0, 246, 255, 0.3);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.4);
}

.audio-toggle-btn:hover:not(:disabled) {
  transform: translateX(3px);
  box-shadow: 0 0 20px rgba(123, 45, 255, 0.5);
}

.audio-toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.volume-indicator {
  height: 6px;
  background: rgba(10, 12, 22, 0.8);
  border: 1px solid rgba(0, 246, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.volume-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary));
  transition: width 0.1s ease;
  box-shadow: 0 0 10px var(--color-accent-primary);
}

.sound-badge {
  background-color: rgba(10, 12, 22, 0.9);
  border: 1px solid var(--color-accent-secondary);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 0 20px rgba(255, 0, 224, 0.5);
  clip-path: polygon(
    0 0,
    calc(100% - 10px) 0,
    100% 10px,
    100% 100%,
    10px 100%,
    0 calc(100% - 10px)
  );
  backdrop-filter: blur(10px);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.9; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

.sound-icon {
  font-size: 1.2rem;
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.sound-text {
  font-size: 0.85rem;
  font-weight: 600;
  font-family: var(--font-display);
  letter-spacing: 2px;
  color: var(--color-accent-secondary);
  text-shadow: 0 0 8px rgba(255, 0, 224, 0.8);
}
</style>
