<template>
  <transition name="slide-fade">
    <div v-if="visible" class="conversation-notification">
      <div class="notification-content">
        <div class="notification-icon">🎯</div>
        <div class="notification-text">
          <div class="notification-title">New conversation created</div>
          <div class="notification-subtitle">{{ conversationTitle }} (from {{ source }})</div>
        </div>
        <button @click="switchToConversation" class="switch-btn">
          Switch
        </button>
        <button @click="dismiss" class="dismiss-btn">
          ✕
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useConversationStore } from '../../stores/conversationStore';

const conversationStore = useConversationStore();

const visible = ref(false);
const conversationId = ref('');
const conversationTitle = ref('');
const source = ref('');
let autoHideTimer = null;

const handleConversationCreated = (event) => {
  conversationId.value = event.detail.conversationId;
  conversationTitle.value = event.detail.conversationTitle;
  source.value = event.detail.source === 'desktop_pet' ? 'Desktop Pet' : event.detail.source;
  
  visible.value = true;
  
  // Auto-hide after 10 seconds
  if (autoHideTimer) clearTimeout(autoHideTimer);
  autoHideTimer = setTimeout(() => {
    visible.value = false;
  }, 10000);
};

const switchToConversation = () => {
  conversationStore.switchConversation(conversationId.value);
  dismiss();
};

const dismiss = () => {
  visible.value = false;
  if (autoHideTimer) clearTimeout(autoHideTimer);
};

onMounted(() => {
  window.addEventListener('conversation:created', handleConversationCreated);
});

onUnmounted(() => {
  window.removeEventListener('conversation:created', handleConversationCreated);
  if (autoHideTimer) clearTimeout(autoHideTimer);
});
</script>

<style scoped>
.conversation-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  max-width: 400px;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(26, 31, 53, 0.95), rgba(14, 16, 27, 0.95));
  border: 1px solid var(--color-accent-primary);
  border-radius: 8px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(0, 246, 255, 0.3);
  backdrop-filter: blur(10px);
}

.notification-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-accent-primary);
  margin-bottom: 4px;
}

.notification-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.switch-btn {
  padding: 8px 16px;
  background: var(--color-accent-primary);
  color: #0E101B;
  border: none;
  border-radius: 4px;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.switch-btn:hover {
  background: #00d4dd;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.5);
  transform: translateY(-1px);
}

.dismiss-btn {
  padding: 4px 8px;
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.dismiss-btn:hover {
  color: var(--color-text-primary);
}

/* Transition animations */
.slide-fade-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.slide-fade-enter-from {
  transform: translateX(100px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100px);
  opacity: 0;
}
</style>
