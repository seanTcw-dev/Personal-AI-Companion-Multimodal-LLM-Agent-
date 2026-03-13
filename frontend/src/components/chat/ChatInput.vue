<template>
  <div class="input-container">
    <input 
      type="file" 
      ref="fileInput" 
      @change="handleFileUpload" 
      accept=".pdf" 
      style="display: none" 
    />
    <button 
      @click="triggerFileUpload" 
      class="attach-button"
      :class="{ 'uploading': isUploading }"
      :title="isUploading ? 'Uploading...' : 'Upload PDF'"
    >
      <svg v-if="!isUploading" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
      </svg>
      <svg v-else class="spin" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="2" x2="12" y2="6"></line>
        <line x1="12" y1="18" x2="12" y2="22"></line>
        <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
        <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
        <line x1="2" y1="12" x2="6" y2="12"></line>
        <line x1="18" y1="12" x2="22" y2="12"></line>
        <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
        <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
      </svg>
    </button>
    <input 
      v-model="newMessage" 
      @keyup.enter="sendMessage"
      @input="handleInput"
      @focus="handleTypingStart"
      :placeholder="chatStore.aiStatusActive && chatStore.isLocalRequest ? 'Waiting for AI response...' : (isListening ? 'Listening...' : (isUploading ? 'Uploading...' : 'Type or Upload PDF...'))" 
      class="message-input" 
      :class="{ 'listening': isListening, 'disabled-input': chatStore.aiStatusActive && chatStore.isLocalRequest }"
      :disabled="isUploading || (chatStore.aiStatusActive && chatStore.isLocalRequest)"
    />
    <button 
      @click="toggleVoiceInput" 
      class="voice-button"
      :class="{ 'listening': isListening, 'error': hasError }"
      :title="isListening ? 'Stop recording' : 'Start voice input'"
    >
      <svg v-if="!isListening" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="23"></line>
        <line x1="8" y1="23" x2="16" y2="23"></line>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <circle cx="12" cy="12" r="10"></circle>
      </svg>
    </button>
    <!-- Send / Stop Button -->
    <button 
      v-if="!chatStore.aiStatusActive || !chatStore.isLocalRequest" 
      @click="sendMessage" 
      class="send-button"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
      <span class="send-text">Send</span>
    </button>
    <button 
      v-else 
      @click="terminateResponse" 
      class="send-button stop-button"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="6" y="6" width="12" height="12" rx="1"></rect>
      </svg>
      <span class="send-text">Stop</span>
    </button>
  </div>
  
  <!-- Voice Input Status Toast -->
  <Transition name="toast">
    <div v-if="showToast" class="voice-toast" :class="toastType">
      {{ toastMessage }}
    </div>
  </Transition>

  <!-- Auto-send Countdown -->
  <Transition name="countdown">
    <div v-if="showCountdown" class="countdown-toast">
      <div class="countdown-content">
        <span class="countdown-text">Sending in {{ countdownSeconds }}s...</span>
        <button @click="cancelAutoSend" class="cancel-btn">✕ Cancel</button>
      </div>
      <div class="countdown-progress" :style="{ width: countdownProgress + '%' }"></div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useChatStore } from '../../stores/chatStore';
import { useConversationStore } from '../../stores/conversationStore';
import { useUIStore } from '../../stores/uiStore';
import { websocketService } from '../../services/websocket';

const chatStore = useChatStore();
const conversationStore = useConversationStore();
const uiStore = useUIStore();
const newMessage = ref('');
const typingTimeoutId = ref(null);
const fileInput = ref(null);
const isUploading = ref(false);
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Voice input state
const isListening = ref(false);
const hasError = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('info');
let recognition = null;
let recognitionTimeout = null;

// Auto-send countdown state
const showCountdown = ref(false);
const countdownSeconds = ref(3);
const countdownProgress = ref(100);
let autoSendTimer = null;
let countdownInterval = null;

// Initialize Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const initSpeechRecognition = () => {
  if (!SpeechRecognition) {
    showToastMessage('Voice input not supported in this browser', 'error');
    return false;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'en-US'; // You can make this configurable
  recognition.continuous = true; // Keep listening until manually stopped
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    console.log('🎤 Voice input started');
    isListening.value = true;
    hasError.value = false;
    showToastMessage('🎤 Listening...', 'info');
  };

  recognition.onresult = (event) => {
    let interimTranscript = '';
    let finalTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }

    // Update input - append final transcripts, show interim
    if (finalTranscript) {
      // Add to existing message if there is one
      if (newMessage.value && !newMessage.value.endsWith(' ')) {
        newMessage.value += ' ';
      }
      newMessage.value += finalTranscript;
      console.log('✅ Final transcript added:', finalTranscript);
      
      // Start countdown for auto-send after final transcript
      if (autoSendTimer) {
        clearTimeout(autoSendTimer);
      }
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
      startAutoSendCountdown();
    } else if (interimTranscript && !finalTranscript) {
      // Show interim results without overwriting
      // (just for visual feedback, don't actually update)
    }
  };

  recognition.onerror = (event) => {
    console.error('❌ Speech recognition error:', event.error);
    
    hasError.value = true;
    let errorMessage = 'Voice input error';
    
    switch(event.error) {
      case 'no-speech':
        errorMessage = 'No speech detected';
        break;
      case 'audio-capture':
        errorMessage = 'No microphone found';
        break;
      case 'not-allowed':
        errorMessage = 'Microphone access denied';
        break;
      case 'network':
        errorMessage = 'Network error';
        break;
      default:
        errorMessage = `Error: ${event.error}`;
    }
    
    showToastMessage(errorMessage, 'error');
    isListening.value = false;
  };

  recognition.onend = () => {
    console.log('🎤 Voice recognition ended');
    
    // Auto-restart if still supposed to be listening (continuous mode)
    if (isListening.value) {
      console.log('🔄 Restarting voice recognition...');
      try {
        recognition.start();
      } catch (error) {
        console.error('Error restarting recognition:', error);
        isListening.value = false;
      }
    }
  };

  return true;
};

// Toggle voice input
const toggleVoiceInput = () => {
  if (!recognition) {
    const initialized = initSpeechRecognition();
    if (!initialized) return;
  }

  if (isListening.value) {
    // Stop listening - user manually turned off
    recognition.stop();
    isListening.value = false;
    showToastMessage('🎤 Voice input stopped', 'info');
    console.log('🛑 User manually stopped voice input');
  } else {
    // Start listening
    hasError.value = false;
    try {
      recognition.start();
      showToastMessage('🎤 Voice input active - Click mic to stop', 'info');
      console.log('▶️ Voice input started (continuous mode)');
    } catch (error) {
      console.error('Error starting recognition:', error);
      // Reinitialize and try again
      recognition = null;
      initSpeechRecognition();
      try {
        recognition.start();
        showToastMessage('🎤 Voice input active - Click mic to stop', 'info');
      } catch (retryError) {
        showToastMessage('Failed to start voice input', 'error');
      }
    }
  }
};

// Show toast message
const showToastMessage = (message, type = 'info') => {
  toastMessage.value = message;
  toastType.value = type;
  showToast.value = true;
  
  // Auto-hide after 3 seconds
  setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

// Start auto-send countdown
const startAutoSendCountdown = () => {
  // Reset countdown
  countdownSeconds.value = 3;
  countdownProgress.value = 100;
  showCountdown.value = true;
  
  console.log('⏱️ Starting 3-second countdown...');
  
  // Update countdown every 100ms for smooth progress bar
  const startTime = Date.now();
  const duration = 3000; // 3 seconds
  
  countdownInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const remaining = Math.max(0, duration - elapsed);
    const secondsLeft = Math.ceil(remaining / 1000);
    
    countdownSeconds.value = secondsLeft;
    countdownProgress.value = (remaining / duration) * 100;
    
    if (remaining <= 0) {
      clearInterval(countdownInterval);
    }
  }, 100);
  
  // Auto-send after 3 seconds
  autoSendTimer = setTimeout(() => {
    if (newMessage.value.trim()) {
      console.log('✅ Auto-sending message...');
      sendMessage();
    }
    showCountdown.value = false;
    clearInterval(countdownInterval);
  }, 3000);
};

// Cancel auto-send
const cancelAutoSend = () => {
  console.log('❌ Auto-send cancelled');
  
  if (autoSendTimer) {
    clearTimeout(autoSendTimer);
    autoSendTimer = null;
  }
  
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
  
  showCountdown.value = false;
  showToastMessage('Auto-send cancelled. Edit your message!', 'info');
};

// Dispatch custom event for typing
const emitTypingEvent = () => {
  window.dispatchEvent(new CustomEvent('chat:typing'));
};

// Handle input changes
const handleInput = () => {
  if (newMessage.value.trim()) {
    emitTypingEvent();
  }
  
  // Cancel auto-send if user starts typing
  if (showCountdown.value) {
    cancelAutoSend();
  }
};

// Handle focus on input
const handleTypingStart = () => {
  emitTypingEvent();
};

// File Upload Logic
const triggerFileUpload = () => {
  if (isUploading.value) return;
  fileInput.value.click();
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  if (file.type !== 'application/pdf') {
    showToastMessage('Only PDF files are supported', 'error');
    return;
  }

  isUploading.value = true;
  showToastMessage(`Uploading ${file.name}...`, 'info');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_URL}/api/files/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Upload failed');

    const data = await response.json();
    console.log('File uploaded:', data);
    
    // Auto-populate message for analysis
    newMessage.value = `Analyze ${file.name} for me.`;
    showToastMessage('File uploaded! Press send to analyze.', 'success');
  } catch (error) {
    console.error('Upload error:', error);
    showToastMessage('Failed to upload file', 'error');
  } finally {
    isUploading.value = false;
    event.target.value = ''; // Reset input
  }
};

// Terminate AI response
const terminateResponse = () => {
  console.log('🛑 User terminated AI response');
  chatStore.setAiStatus('idle', '');
  websocketService.terminateResponse();
  showToastMessage('Response terminated', 'info');
};

const sendMessage = async () => {
  // Block sending while AI is processing
  if (chatStore.aiStatusActive) return;
  if (newMessage.value.trim()) {
    // Cancel auto-send countdown if active
    if (showCountdown.value) {
      if (autoSendTimer) {
        clearTimeout(autoSendTimer);
      }
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
      showCountdown.value = false;
    }
    
    // DON'T stop voice input - let it continue listening
    // User can manually click mic button to stop
    
    // Call the Pinia store action to send the message
    chatStore.sendMessage(newMessage.value);
    
    // Send the message through the WebSocket service
    websocketService.sendMessage({
      text: newMessage.value
    });
    
    // Show the dialogue ticker
    uiStore.setDialogueTickerVisibility(true);
    
    // Clear the input
    newMessage.value = '';
    
    // Refresh conversation list after a short delay to update title/create new chat
    setTimeout(async () => {
      await conversationStore.loadConversations();
      
      // If we were in "New Chat" mode (no active ID), switch to the newest conversation
      // This ensures the title updates from "New Chat" to the auto-generated name
      if (!conversationStore.activeConversationId && conversationStore.sortedConversations.length > 0) {
        const newestConv = conversationStore.sortedConversations[0];
        console.log('👉 Auto-switched to new conversation:', newestConv.title);
        conversationStore.switchConversation(newestConv.id);
        
        // Also notify backend that this is now the active conversation
        try {
            const userId = conversationStore.userId;
            await fetch(`http://localhost:8000/api/conversations/${newestConv.id}/activate?user_id=${userId}`, {
                method: 'POST'
            });
        } catch (e) {
            console.error('Failed to activate new conversation:', e);
        }
      }
      
      console.log('🔄 Refreshed conversation list');
    }, 1500); // Increased wait time to ensure Ollama processing & renaming is done
  }
};

// Cleanup on unmount
onUnmounted(() => {
  if (recognition && isListening.value) {
    recognition.stop();
  }
  
  if (autoSendTimer) {
    clearTimeout(autoSendTimer);
  }
  
  if (countdownInterval) {
    clearInterval(countdownInterval);
  }
});
</script>

<style scoped>
.input-container {
  display: flex;
  padding: 0.75rem;
  background-color: transparent;
  width: 100%;
  position: relative;
  z-index: 5;
  gap: 0.5rem;
}

.message-input {
  flex: 1;
  padding: 0.7rem 0.9rem;
  border: 1px solid var(--color-accent-primary);
  border-radius: 0;
  background-color: rgba(14, 16, 27, 0.6);
  color: var(--color-text-primary);
  transition: all 0.3s ease;
  font-family: var(--font-body);
  font-size: 0.95rem;
  clip-path: polygon(0 0, 100% 0, calc(100% - 10px) 100%, 0 100%);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.2);
}

.message-input.listening {
  border-color: #f5576c;
  box-shadow: 0 0 20px rgba(245, 87, 108, 0.6);
  animation: pulse-border 1.5s infinite;
}

@keyframes pulse-border {
  0%, 100% {
    box-shadow: 0 0 15px rgba(245, 87, 108, 0.4);
  }
  50% {
    box-shadow: 0 0 25px rgba(245, 87, 108, 0.8);
  }
}

.message-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.4), inset 0 0 10px rgba(0, 246, 255, 0.1);
  background-color: rgba(14, 16, 27, 0.8);
}

.message-input.listening:focus {
  border-color: #f5576c;
  box-shadow: 0 0 25px rgba(245, 87, 108, 0.8);
}

.message-input::placeholder {
  color: var(--color-text-secondary);
  opacity: 0.7;
  font-family: var(--font-body);
  font-style: italic;
}



.attach-button {
  padding: 0.7rem 0.9rem;
  background: rgba(14, 16, 27, 0.6);
  color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(
    6px 0,
    100% 0,
    100% calc(100% - 6px),
    calc(100% - 6px) 100%,
    0 100%,
    0 6px
  );
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.attach-button:hover {
  background: rgba(14, 16, 27, 0.8);
  color: #fff;
  border-color: #fff;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
}

.attach-button.uploading {
  cursor: wait;
  opacity: 0.7;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.voice-button {
  padding: 0.7rem 0.9rem;
  background: linear-gradient(135deg, rgba(0, 246, 255, 0.15) 0%, rgba(123, 45, 255, 0.15) 100%);
  color: var(--color-accent-primary);
  border: 1px solid var(--color-accent-primary);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(
    6px 0,
    100% 0,
    100% calc(100% - 6px),
    calc(100% - 6px) 100%,
    0 100%,
    0 6px
  );
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3);
}

.voice-button:hover {
  background: linear-gradient(135deg, rgba(0, 246, 255, 0.25) 0%, rgba(123, 45, 255, 0.25) 100%);
  transform: translateY(-1px);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.5);
}

.voice-button.listening {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-color: #f5576c;
  animation: pulse-mic 1.5s infinite;
}

@keyframes pulse-mic {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 15px rgba(245, 87, 108, 0.5);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(245, 87, 108, 0.8);
  }
}

.voice-button.error {
  border-color: #ff5252;
  color: #ff5252;
}

.voice-button svg {
  filter: drop-shadow(0 0 2px rgba(0, 246, 255, 0.8));
}

.voice-button.listening svg {
  filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.9));
}

.send-button {
  padding: 0.7rem 1.2rem;
  background: linear-gradient(135deg, var(--color-accent-primary) 0%, var(--color-accent-tertiary) 100%);
  color: white;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 0.9rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
  clip-path: polygon(
    8px 0,
    100% 0,
    100% calc(100% - 8px),
    calc(100% - 8px) 100%,
    0 100%,
    0 8px
  );
}

.send-button::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, var(--color-accent-primary), var(--color-accent-tertiary));
  z-index: -1;
  filter: blur(10px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.send-button svg {
  filter: drop-shadow(0 0 2px rgba(255, 255, 255, 0.8));
  transition: all 0.3s ease;
}

.send-button:hover {
  background: linear-gradient(135deg, var(--color-accent-tertiary) 0%, var(--color-accent-primary) 100%);
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.6);
}

.send-button:hover::before {
  opacity: 1;
}

.send-button:hover svg {
  transform: rotate(-10deg);
  filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.9));
}

.send-button:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3);
}

.send-text {
  text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

/* Stop Button Override */
.stop-button {
  background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%) !important;
  box-shadow: 0 0 15px rgba(255, 68, 68, 0.4) !important;
  animation: stop-pulse 1.5s infinite;
}

.stop-button:hover {
  background: linear-gradient(135deg, #ff6666 0%, #ff2222 100%) !important;
  box-shadow: 0 0 20px rgba(255, 68, 68, 0.6) !important;
}

@keyframes stop-pulse {
  0%, 100% { box-shadow: 0 0 15px rgba(255, 68, 68, 0.4); }
  50% { box-shadow: 0 0 25px rgba(255, 68, 68, 0.7); }
}

/* Disabled input when AI is processing */
.disabled-input {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
}

/* Voice Toast Notification */
.voice-toast {
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  pointer-events: none;
}

.voice-toast.info {
  background: rgba(0, 246, 255, 0.9);
  color: #0E101B;
  border: 1px solid rgba(0, 246, 255, 1);
}

.voice-toast.success {
  background: rgba(76, 175, 80, 0.9);
  color: white;
  border: 1px solid rgba(76, 175, 80, 1);
}

.voice-toast.error {
  background: rgba(255, 82, 82, 0.9);
  color: white;
  border: 1px solid rgba(255, 82, 82, 1);
}

/* Toast animation */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

/* Countdown Toast */
.countdown-toast {
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 246, 255, 0.95);
  border: 2px solid var(--color-accent-primary);
  border-radius: 12px;
  padding: 0;
  z-index: 1001;
  box-shadow: 0 0 25px rgba(0, 246, 255, 0.6);
  backdrop-filter: blur(10px);
  min-width: 300px;
  overflow: hidden;
}

.countdown-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  gap: 12px;
}

.countdown-text {
  color: #0E101B;
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.countdown-text::before {
  content: '⏱️';
  font-size: 1.2rem;
  animation: countdown-pulse 1s infinite;
}

@keyframes countdown-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

.cancel-btn {
  background: rgba(255, 82, 82, 0.9);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.cancel-btn:hover {
  background: rgba(255, 82, 82, 1);
  transform: scale(1.05);
}

.cancel-btn:active {
  transform: scale(0.95);
}

.countdown-progress {
  height: 4px;
  background: linear-gradient(90deg, var(--color-accent-tertiary), var(--color-accent-primary));
  transition: width 0.1s linear;
  box-shadow: 0 0 10px rgba(123, 45, 255, 0.8);
}

/* Countdown animation */
.countdown-enter-active {
  transition: all 0.3s ease;
}

.countdown-leave-active {
  transition: all 0.2s ease;
}

.countdown-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(30px) scale(0.9);
}

.countdown-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px) scale(0.95);
}
</style>