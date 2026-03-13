<template>
  <div class="main-layout">
    <!-- Column 1: Chat Sidebar -->
    <ChatSidebar />

    <!-- Column 2: Main Interaction Area -->
    <div class="column main-interaction-column">
      <!-- Conversation Title Header -->
      <div class="conversation-header">
        <div v-if="isEditingTitle" class="title-edit-container">
          <input 
            ref="titleInputRef"
            v-model="editedTitle"
            @blur="saveTitle"
            @keyup.enter="saveTitle"
            class="title-input"
            type="text"
          />
        </div>
        <h2 
          v-else 
          class="conversation-title" 
          @click="startEditing"
          title="Click to rename"
        >
          {{ activeConversationTitle }}
          <span class="edit-hint">✎</span>
        </h2>
      </div>
      
      <div class="main-stage">
        <div class="dialogue-window">
          <CharacterView ref="characterViewRef" />
        </div>
        <!-- Add the DialogueTicker component -->
        <DialogueTicker />
      </div>

      <div class="chat-input-area">
        <ChatInput />
      </div>
    </div>

    <!-- Column 3: Camera Feed -->
    <div class="column camera-feed-column">
      <div class="character-status">
        <div class="status-indicator"></div>
        <span>Ai Assistant - Online</span>
      </div>

      <CameraView />
    </div>
    
    <!-- Conversation notification toast -->
    <ConversationNotification />

    <!-- Global camera shutter flash overlay (lives here to escape clip-path containers) -->
    <div class="shutter-flash" :class="{ active: shutterFlash }"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed, nextTick } from 'vue';
import ChatInput from '../chat/ChatInput.vue';
import ChatSidebar from '../chat/ChatSidebar.vue';
import CharacterView from '../character/CharacterView.vue';
import CameraView from '../camera/CameraView.vue';
import DialogueTicker from '../chat/DialogueTicker.vue';
import ConversationNotification from '../chat/ConversationNotification.vue';
import { useChatStore } from '../../stores/chatStore';
import { useConversationStore } from '../../stores/conversationStore';
import { useUIStore } from '../../stores/uiStore';
import { initializeWebSocket } from '../../services/websocketInit';
import { useRoute, useRouter } from 'vue-router';

const characterViewRef = ref(null);
const chatStore = useChatStore();
const conversationStore = useConversationStore();
const uiStore = useUIStore();
const route = useRoute();
const router = useRouter();

// ====== Global Shutter Flash ======
const shutterFlash = ref(false);

const playShutterSound = () => {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const bufferSize = ctx.sampleRate * 0.08;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 8);
    }
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 3000;
    filter.Q.value = 0.5;
    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(1.5, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
    source.connect(filter);
    filter.connect(gainNode);
    gainNode.connect(ctx.destination);
    source.start();
  } catch (e) {
    console.warn('Shutter sound unavailable:', e);
  }
};

const onShutterEvent = () => {
  playShutterSound();
  shutterFlash.value = true;
  setTimeout(() => { shutterFlash.value = false; }, 400);
};

// Lip sync event handler — forward volume to CharacterView
const onLipSyncVolume = (event) => {
  if (characterViewRef.value && characterViewRef.value.updateLipSync) {
    characterViewRef.value.updateLipSync(event.detail.volume);
  }
};

onMounted(() => {
  // Listen for shutter event from CameraView
  window.addEventListener('camera:shutter', onShutterEvent);

  // Listen for lip sync volume events and forward to character
  window.addEventListener('lipsync:volume', onLipSyncVolume);

  // Initialize WebSocket connection when entering the main chat view
  initializeWebSocket();

  // Set initial emotion if needed
  if (characterViewRef.value && chatStore.currentEmotion) {
    characterViewRef.value.setExpression(chatStore.currentEmotion);
  }

  // --- POST-LOGIN TRANSITION LOGIC ---
  if (route.query.transition === 'true') {
    // 1. Hide "Quick Cards" / History initially
    uiStore.setDialogueTickerVisibility(false);
    
    // 2. Play Greeting Audio after 5 seconds, with waving animation and happy expression
    setTimeout(() => {
      const audio = new Audio('/sound effect/After Flash Greeting message.mp3');
      audio.volume = 0.6;
      audio.play().catch(e => console.error("Greeting audio failed:", e));
      
      // Trigger waving animation
      if (characterViewRef.value && characterViewRef.value.playWave) {
        characterViewRef.value.playWave();
      }
      
      // Set happy/joy expression
      if (characterViewRef.value && characterViewRef.value.setExpression) {
        characterViewRef.value.setExpression('happy', 1.0);
      }
    }, 3500); // 5 seconds delay

    // 3. Clean URL
    router.replace({ query: null });
  }
});
const editedTitle = ref('');
const titleInputRef = ref(null);
const isEditingTitle = ref(false);

const startEditing = async () => {
  // Only allow editing if there is an active conversation
  if (conversationStore.activeConversation) {
    editedTitle.value = activeConversationTitle.value;
    isEditingTitle.value = true;
    await nextTick();
    if (titleInputRef.value) {
      titleInputRef.value.focus();
    }
  }
};

const saveTitle = async () => {
  if (isEditingTitle.value && editedTitle.value.trim()) {
    const newTitle = editedTitle.value.trim();
    if (newTitle !== activeConversationTitle.value) {
      await conversationStore.renameConversation(
        conversationStore.activeConversation.id, 
        newTitle
      );
    }
    isEditingTitle.value = false;
  } else {
    cancelEditing();
  }
};

const cancelEditing = () => {
  isEditingTitle.value = false;
  editedTitle.value = activeConversationTitle.value;
};

// Computed properties for conversation title
const activeConversationTitle = computed(() => {
  const activeConv = conversationStore.activeConversation;
  return activeConv ? activeConv.title : 'New Chat';
});

const activeConversationMessageCount = computed(() => {
  const activeConv = conversationStore.activeConversation;
  return activeConv ? (activeConv.message_count || 0) : chatStore.messages.length;
});

const isHistoryVisible = computed(() => uiStore.isDialogueTickerVisible);

// Toggle conversation history
const toggleConversationHistory = () => {
  uiStore.setDialogueTickerVisibility(!uiStore.isDialogueTickerVisible);
};

// Watch for changes in the current emotion and update the character's expression
watch(() => chatStore.currentEmotion, (newEmotion) => {
  if (characterViewRef.value && newEmotion) {
    characterViewRef.value.setExpression(newEmotion);
  }
});

onMounted(() => {
  // Set initial emotion if needed
  if (characterViewRef.value && chatStore.currentEmotion) {
    characterViewRef.value.setExpression(chatStore.currentEmotion);
  }
});

import { onBeforeUnmount } from 'vue';
onBeforeUnmount(() => {
  window.removeEventListener('camera:shutter', onShutterEvent);
  window.removeEventListener('lipsync:volume', onLipSyncVolume);
});
</script>



<style scoped>
:global(:root) {
  /* Cyberpunk anime color palette */
  --color-bg-primary: #0E101B; /* Deep space black with slight blue tint */
  --color-bg-secondary: #1A1F35; /* Dark navy blue */
  --color-bg-tertiary: #171624; /* Dark purple-black */
  
  --color-text-primary: #E8EDFF; /* Soft white with blue tint */
  --color-text-secondary: #9FADC6; /* Muted lavender */
  
  /* Vibrant accent colors */
  --color-accent-primary: #00F6FF; /* Vibrant cyan */
  --color-accent-secondary: #FF00E0; /* Hot pink */
  --color-accent-tertiary: #7B2DFF; /* Bright purple */
  
  --color-border: rgba(0, 246, 255, 0.3); /* Semi-transparent cyan */
  --shadow-soft: 0 4px 12px rgba(0, 246, 255, 0.15);
  --glow-primary: 0 0 15px rgba(0, 246, 255, 0.6);
  --glow-secondary: 0 0 15px rgba(255, 0, 224, 0.6);
  
  /* Typography */
  --font-display: 'Orbitron', 'Rajdhani', sans-serif;
  --font-body: 'Inter', 'Roboto', sans-serif;
}

:global(*, *::before, *::after) {
  box-sizing: border-box;
}

/* Basic CSS Reset applied to the component's scope */
:global(html), :global(body) {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden; /* Prevents scrollbars */
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
  font-family: var(--font-body);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect x="0" y="0" width="100" height="100" fill="none" stroke="%2300F6FF20" stroke-width="0.5"/><line x1="0" y1="0" x2="100" y2="100" stroke="%2300F6FF10" stroke-width="0.5"/><line x1="100" y1="0" x2="0" y2="100" stroke="%2300F6FF10" stroke-width="0.5"/></svg>');
  background-size: 50px 50px;
}

/* 1. Make the main layout fill the entire browser window */
.main-layout {
  display: flex;
  width: 100%; /* Changed from 100vw to prevent horizontal overflow */
  height: 100vh; /* 100% of viewport height */
  background-color: var(--color-bg-primary); /* Dark background */
  overflow: hidden; /* Prevent content from causing scrollbars */
  margin: 0; /* Ensure no margins on the main container */
  position: absolute; /* Position absolutely to fill the viewport */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.column {
  /* Basic styling for columns - you can adjust padding */
  padding: 1rem;
  height: 100%; /* Make columns take full height of the layout */
  box-sizing: border-box; /* Ensures padding is included in height/width */
}

/* Navigation column styling */
.navigation-column {
  flex-basis: 250px; /* Width */
  flex-shrink: 0; /* Prevent this column from shrinking */
  background-color: rgba(26, 31, 53, 0.8); /* Semi-transparent */
  overflow-y: auto; /* Allow scrolling if content is too tall */
  position: relative;
  backdrop-filter: blur(10px); /* Glass effect */
  -webkit-backdrop-filter: blur(10px);
  border-right: none;
  box-shadow: 5px 0 15px rgba(0, 0, 0, 0.3);
  z-index: 5;
  clip-path: polygon(
    0 0,
    calc(100% - 15px) 0,
    100% 15px,
    100% 100%,
    0 100%
  );
  display: flex;
  flex-direction: column;
  padding: 0; /* Remove padding to customize inner components */
}

/* App logo styling */
.app-logo {
  display: flex;
  align-items: center;
  padding: 1.2rem 1rem;
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
  margin-bottom: 1rem;
}

.app-logo img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
  filter: drop-shadow(0 0 8px var(--color-accent-primary));
}

.app-logo h1 {
  margin: 0;
  font-size: 1.2rem;
  font-family: var(--font-display);
  color: var(--color-accent-primary);
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 0 0 10px rgba(0, 246, 255, 0.6);
}

/* Navigation buttons styling */
.nav-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0 1rem 1rem 1rem;
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
}

.nav-btn {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(10, 12, 22, 0.6);
  border: 1px solid rgba(0, 246, 255, 0.3);
  color: var(--color-text-primary);
  font-family: var(--font-body);
  cursor: pointer;
  transition: all 0.3s ease;
  clip-path: polygon(0 0, 100% 0, calc(100% - 10px) 100%, 0 100%);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.nav-btn svg {
  margin-right: 10px;
  color: var(--color-accent-primary);
}

.nav-btn:hover, .nav-btn.active {
  background: rgba(0, 246, 255, 0.15);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.3);
}

/* Chat history list styling */
.chat-history-list {
  padding: 1rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.chat-history-list h2 {
  font-size: 0.9rem;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  margin: 0 0 1rem 0;
  font-family: var(--font-heading);
  letter-spacing: 1px;
}

.chat-hist.conversation-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.history-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 246, 255, 0.1);
  border: 1px solid var(--color-accent-primary);
  color: var(--color-accent-primary);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 0.85rem;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.history-btn:hover {
  background: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3);
  transform: translateY(-1px);
}

.history-btn.active {
  background: var(--color-accent-primary);
  color: #0E101B;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.5);
}

.history-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.history-btn:hover::before {
  left: 100%;
}

.message-count {
  font-size: 13px;
  color: var(--color-text-secondary);
  padding: 5px 10px;
  background: rgba(10, 12, 22, 0.6);
  border: 1px solid rgba(0, 246, 255, 0.3);
  border-radius: 12px;
  font-weight: 500;
}


.chat-history-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow-y: auto;
}

.chat-history-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(10, 12, 22, 0.4);
  border: 1px solid rgba(0, 246, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  clip-path: polygon(0 0, 100% 0, calc(100% - 8px) 100%, 0 100%);
}

.chat-history-item:hover {
  background: rgba(0, 246, 255, 0.1);
  border-color: rgba(0, 246, 255, 0.3);
  transform: translateX(5px);
}

.chat-icon {
  width: 28px;
  height: 28px;
  border-radius: 0;
  background: rgba(0, 246, 255, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 10px;
  color: var(--color-accent-primary);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
}

.chat-details {
  flex: 1;
}

.chat-title {
  font-size: 0.9rem;
  color: var(--color-text-primary);
  margin-bottom: 3px;
}

.chat-date {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  opacity: 0.8;
}

.camera-feed-column {
  flex-basis: 300px; /* Example width */
  flex-shrink: 0; /* Prevent this column from shrinking */
  background-color: rgba(23, 22, 36, 0.8); /* Semi-transparent */
  color: var(--color-text-primary);
  overflow: hidden; /* Contain all content within this column */
  border-left: none;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.3), inset 0 0 20px rgba(0, 0, 0, 0.4);
  position: relative;
  backdrop-filter: blur(10px); /* Glass effect */
  -webkit-backdrop-filter: blur(10px);
  z-index: 5;
  clip-path: polygon(
    15px 0,
    100% 0,
    100% 100%,
    0 100%,
    0 15px
  );
}

.camera-feed-column::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 0, 224, 0.05) 0%, transparent 50%, rgba(0, 246, 255, 0.05) 100%);
  z-index: -1;
}

.camera-feed-column::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--color-accent-secondary), transparent);
  box-shadow: 0 0 15px var(--color-accent-secondary);
  z-index: 10;
}

/* Conversation Header Styles */
/* Conversation Header Styles */
.conversation-header {
  padding-top: 8px; /* Reduced from 50px */
  padding-bottom: 0px; /* Reduced from 20px */
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  /* Minimal background separation */
  background: linear-gradient(to bottom, rgba(11, 13, 20, 0.8) 0%, rgba(11, 13, 20, 0) 100%);
  z-index: 10;
}

.conversation-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(45deg, var(--color-accent-primary), var(--color-accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.conversation-title:hover {
  text-shadow: 0 0 25px rgba(0, 246, 255, 0.5);
  transform: scale(1.02);
}

.edit-hint {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
  vertical-align: middle;
  -webkit-text-fill-color: initial;
}

.conversation-title:hover .edit-hint {
  opacity: 1;
}

.title-edit-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.title-input {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  text-align: center;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--color-accent-primary);
  border-radius: 4px;
  padding: 4px 12px;
  outline: none;
  width: 80%;
  max-width: 600px;
  min-width: 300px;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.2);
}

.title-input:focus {
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.4);
}

/* 2. Fix the layout of the Main Interaction Column */
.main-interaction-column {
  /* This column should take up the rest of the space */
  flex-grow: 1; 
  
  /* Make it a vertical flex container */
  display: flex;
  flex-direction: column;

  /* Remove padding to allow content to go edge-to-edge within the column */
  padding: 0; 
  position: relative;
  z-index: 1;
  overflow: hidden;
}

/* Main stage container for character view */
.main-stage {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background-color: var(--color-bg-primary);
}

/* Dialogue window container */
.dialogue-window {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* Chat messages area styling */
.chat-messages-area {
  /* Will be replaced by dialogue-window, keeping for compatibility */
  display: none;
}

.main-interaction-column::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(14, 16, 27, 0.3) 0%, rgba(14, 16, 27, 0.9) 100%);
  z-index: -1;
}

.character-stage {
  /* Will be replaced by main-stage, keeping for compatibility */
  display: none;
}

/* Dynamic background with particles effect */
.character-stage::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(0, 246, 255, 0.1) 0%, rgba(123, 45, 255, 0.05) 70%);
  z-index: 0;
  animation: pulse 10s infinite alternate;
}

/* Grid overlay for cyberpunk effect */
.character-stage::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: linear-gradient(0deg, transparent 24%, rgba(0, 246, 255, 0.05) 25%, rgba(0, 246, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 246, 255, 0.05) 75%, rgba(0, 246, 255, 0.05) 76%, transparent 77%, transparent),
                    linear-gradient(90deg, transparent 24%, rgba(0, 246, 255, 0.05) 25%, rgba(0, 246, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 246, 255, 0.05) 75%, rgba(0, 246, 255, 0.05) 76%, transparent 77%, transparent);
  background-size: 50px 50px;
  z-index: 0;
}

/* Character status badge */
.character-status {
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: rgba(10, 12, 23, 0.8);
  border-radius: 0;
  padding: 6px 12px;
  color: var(--color-accent-primary);
  font-size: 0.7rem;
  font-family: var(--font-display);
  display: flex;
  align-items: center;
  z-index: 10;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 5% 100%);
  border-right: 2px solid var(--color-accent-primary);
  box-shadow: var(--glow-primary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-accent-primary); /* Cyan for online */
  margin-right: 12px;
  box-shadow: 0 0 8px var(--color-accent-primary);
  animation: breathe 2s infinite ease-in-out;
}

@keyframes breathe {
  0% { opacity: 0.5; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0.5; transform: scale(0.8); }
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 0.8; }
  100% { opacity: 0.5; }
}

.chat-input-area {
  /* This will be pushed to the bottom */
  flex-shrink: 0; /* Prevents this area from shrinking */
  padding: 1rem;
  background-color: rgba(23, 22, 36, 0.8); /* Semi-transparent background */
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  width: 100%; /* Ensure it takes full width */
  border-top: none; /* Remove border */
  position: relative;
  z-index: 0;  /* Bottom layer - character will stand on this */
  clip-path: polygon(
    0 0,
    15px 0,
    100% 0,
    100% 100%,
    0 100%
  );
  box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.3);
}

.chat-input-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--color-accent-primary), transparent);
  box-shadow: 0 0 10px var(--color-accent-primary);
}

.chat-input-area input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.chat-input-area input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 2px rgba(0, 191, 255, 0.2);
}



/* Media queries for responsive layout */
@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
  }
  
  .column {
    width: 100%;
  }
  
  .navigation-column {
    height: auto;
    flex-basis: auto;
    clip-path: none;
  }
  
  .main-interaction-column {
    height: 50vh;
  }
  
  .camera-feed-column {
    height: 30vh;
    flex-basis: auto;
  }
  
  .character-stage {
    min-height: 25vh;
  }
  
  .chat-messages-area {
    height: 15vh;
  }
}

/* ====== Global Shutter Flash ====== */
.shutter-flash {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background: white;
  z-index: 99999;
  pointer-events: none;
  opacity: 0;
}

.shutter-flash.active {
  animation: shutter-snap 0.4s ease-out forwards;
}

@keyframes shutter-snap {
  0%   { opacity: 0.85; }
  25%  { opacity: 0.5; }
  100% { opacity: 0; }
}
</style>