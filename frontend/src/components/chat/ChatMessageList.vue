<template>
  <div class="messages-container">
    
    <!-- Messages list with animation -->
    <transition-group name="message-transition">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        class="message" 
        :class="message.sender"
      >
        <div class="message-content">
          {{ message.text }}
        </div>
        <div class="message-actions">
          <button title="Copy message" class="action-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path>
            </svg>
          </button>
        </div>
      </div>
    </transition-group>

    <!-- AI Status Indicator (only show when THIS window initiated the request, not Desktop Pet) -->
    <Transition name="status-slide">
      <div v-if="chatStore.aiStatusActive && chatStore.isLocalRequest" class="ai-status-bar">
        <div class="ai-status-indicator">
          <div class="status-dot-pulse"></div>
          <span class="status-text">{{ chatStore.aiStatus }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, watch, nextTick, ref } from 'vue';
import { useChatStore } from '../../stores/chatStore';

const chatStore = useChatStore();
// Use computed property to ensure reactivity
const messages = computed(() => chatStore.messages);

// Auto-scroll to bottom when status appears or messages change
const containerRef = ref(null);
const scrollToBottom = async () => {
  await nextTick();
  const container = document.querySelector('.messages-container');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
};
watch(() => chatStore.aiStatusActive, scrollToBottom);
watch(() => chatStore.messages.length, scrollToBottom);
</script>

<style scoped>
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: transparent;
  scrollbar-width: thin;
  scrollbar-color: var(--color-accent-primary) transparent;
  position: relative;
  z-index: 5;
}

/* Scrollbar styling */
.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.messages-container::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, var(--color-accent-primary), var(--color-accent-tertiary));
  border-radius: 0;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, var(--color-accent-tertiary), var(--color-accent-primary));
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.5);
}

/* Message animations */
.message-transition-enter-active {
  transition: all 0.5s ease;
}

.message-transition-leave-active {
  transition: all 0.5s ease;
}

.message-transition-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-transition-leave-to {
  opacity: 0;
}

/* Message styling */
.message {
  position: relative;
  margin-bottom: 1rem;
  max-width: 80%;
  padding: 0.75rem;
  border-radius: 0; /* Sharp corners for cyberpunk style */
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  font-family: var(--font-body);
}

.message:hover {
  transform: translateY(-2px);
}

.message.user:hover {
  box-shadow: 0 5px 20px rgba(0, 246, 255, 0.4), inset 0 0 20px rgba(0, 246, 255, 0.15);
}

.message.ai:hover {
  box-shadow: 0 5px 20px rgba(123, 45, 255, 0.3), inset 0 0 15px rgba(123, 45, 255, 0.15);
}

.message.user {
  align-self: flex-end;
  background: linear-gradient(135deg, rgba(0, 246, 255, 0.3) 0%, rgba(0, 130, 175, 0.5) 100%);
  color: #FFFFFF;
  border-right: 2px solid var(--color-accent-primary);
  box-shadow: 0 2px 10px rgba(0, 246, 255, 0.2), inset 0 0 20px rgba(0, 246, 255, 0.1);
  clip-path: polygon(
    0 0,
    100% 0,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    0 100%
  );
  position: relative;
  overflow: visible;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

.message.user::after {
  content: '';
  position: absolute;
  top: -1px;
  right: -1px;
  bottom: -1px;
  left: -1px;
  background: linear-gradient(135deg, rgba(0, 246, 255, 0.5) 0%, rgba(0, 130, 175, 0.3) 100%);
  z-index: -1;
  filter: blur(10px);
  opacity: 0.5;
  clip-path: polygon(
    0 0,
    100% 0,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    0 100%
  );
}

.message.ai {
  align-self: flex-start;
  background: linear-gradient(135deg, rgba(123, 45, 255, 0.3) 0%, rgba(40, 44, 65, 0.8) 100%);
  color: var(--color-text-primary);
  border-left: 2px solid var(--color-accent-secondary);
  box-shadow: 0 2px 10px rgba(123, 45, 255, 0.2), inset 0 0 15px rgba(123, 45, 255, 0.1);
  clip-path: polygon(
    0 0,
    100% 0,
    100% 100%,
    12px 100%,
    0 calc(100% - 12px)
  );
  position: relative;
  overflow: visible;
}

.message.ai::after {
  content: '';
  position: absolute;
  top: -1px;
  right: -1px;
  bottom: -1px;
  left: -1px;
  background: linear-gradient(135deg, rgba(123, 45, 255, 0.4) 0%, rgba(40, 44, 65, 0.3) 100%);
  z-index: -1;
  filter: blur(10px);
  opacity: 0.5;
  clip-path: polygon(
    0 0,
    100% 0,
    100% 100%,
    12px 100%,
    0 calc(100% - 12px)
  );
}

.message-content {
  line-height: 1.5;
}

.message-actions {
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message:hover .message-actions {
  opacity: 1;
}

.action-button {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: inherit;
  opacity: 0.6;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0;
  transition: all 0.2s ease;
}

.action-button:hover {
  opacity: 1;
  background: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3);
  transform: scale(1.1);
}

/* AI Status Indicator */
.ai-status-bar {
  align-self: flex-start;
  padding: 8px 16px;
  margin-bottom: 0.5rem;
  background: rgba(10, 12, 22, 0.6);
  border-left: 2px solid var(--color-accent-primary);
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.1);
}

.ai-status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot-pulse {
  position: relative;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-accent-primary);
  box-shadow: 0 0 8px var(--color-accent-primary);
  animation: status-pulse 1.2s ease-in-out infinite;
}

.status-dot-pulse::before,
.status-dot-pulse::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-accent-primary);
  transform: translate(-50%, -50%);
  opacity: 0;
}

.status-dot-pulse::before {
  animation: status-ripple 1.2s ease-out infinite;
}

.status-dot-pulse::after {
  animation: status-ripple 1.2s ease-out infinite 0.4s;
}

@keyframes status-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.8); }
}

@keyframes status-ripple {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(3.5); opacity: 0; }
}

.status-text {
  font-family: var(--font-display);
  font-size: 0.72rem;
  color: var(--color-accent-primary);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  text-shadow: 0 0 8px rgba(0, 246, 255, 0.4);
  animation: status-text-glow 2s ease-in-out infinite;
}

@keyframes status-text-glow {
  0%, 100% { text-shadow: 0 0 5px rgba(0, 246, 255, 0.3); }
  50% { text-shadow: 0 0 15px rgba(0, 246, 255, 0.7), 0 0 30px rgba(0, 246, 255, 0.3); }
}

/* Status slide transition */
.status-slide-enter-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.status-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease-in;
}

.status-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.status-slide-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>