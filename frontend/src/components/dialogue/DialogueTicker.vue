<template>
  <div v-if="uiStore.isDialogueTickerVisible" class="dialogue-ticker">
    <button @click="closeDialogueTicker" class="close-btn" aria-label="Close dialogue">
      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
    <div class="ticker-content">
      <ChatMessageList />
    </div>
  </div>
</template>

<script setup>
import { useUIStore } from '../../stores/uiStore';
import ChatMessageList from '../chat/ChatMessageList.vue';

const uiStore = useUIStore();

// Function to close the dialogue ticker
const closeDialogueTicker = () => {
  uiStore.setDialogueTickerVisibility(false);
};
</script>

<style scoped>
.dialogue-ticker {
  position: absolute;
  bottom: 100px; /* Position just above the chat input */
  left: 50%;
  transform: translateX(-50%);
  width: 60vw;
  max-height: 180px;
  background-color: rgba(17, 22, 35, 0.75);
  z-index: 50;
  overflow: hidden;
  animation: tickerAppear 0.3s ease-out forwards;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
  border-top: 2px solid;
  border-image: linear-gradient(90deg, rgba(0, 246, 255, 0.6), rgba(123, 45, 255, 0.6)) 1;
  backdrop-filter: blur(5px);
}

@keyframes tickerAppear {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.close-btn {
  position: absolute;
  right: 8px;
  top: 8px;
  background: rgba(10, 12, 22, 0.6);
  border: 1px solid rgba(0, 246, 255, 0.2);
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--color-accent-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  z-index: 2;
}

.close-btn:hover {
  background-color: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 8px rgba(0, 246, 255, 0.5);
  transform: scale(1.1);
}

.ticker-content {
  height: 100%;
  max-height: 180px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--color-accent-primary) rgba(0, 0, 0, 0.2);
}

.ticker-content::-webkit-scrollbar {
  width: 4px;
}

.ticker-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.ticker-content::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, var(--color-accent-primary), var(--color-accent-tertiary));
  border-radius: 0;
}

.ticker-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, var(--color-accent-tertiary), var(--color-accent-primary));
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.5);
}

/* Override some ChatMessageList styles to fit inside the ticker */
:deep(.messages-container) {
  padding: 0.5rem 1rem 1rem;
  height: auto;
}

:deep(.message) {
  margin-bottom: 0.5rem;
  max-width: 90%;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
}

/* Add a subtle info bar at the top */
.ticker-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-tertiary));
  opacity: 0.6;
}
</style>