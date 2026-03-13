<template>
  <Transition name="slide-up">
    <div v-if="isVisible" class="dialogue-ticker">
      <div class="dialogue-ticker-header">
        <div class="dialogue-ticker-title">CONVERSATION HISTORY</div>
        <button class="dialogue-ticker-close" @click="closeDialogueTicker">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <ChatMessageList class="dialogue-messages" />
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue';
import { useUIStore } from '../../stores/uiStore';
import ChatMessageList from './ChatMessageList.vue';

const uiStore = useUIStore();

// Computed property to get the visibility state from the store
const isVisible = computed(() => uiStore.isDialogueTickerVisible);

// Method to close the dialogue ticker
const closeDialogueTicker = () => {
  uiStore.setDialogueTickerVisibility(false);
};
</script>

<style scoped>
.dialogue-ticker {
  position: absolute;
  bottom: 15px; /* Adjusted: positioned lower, just above the green line at bottom */
  left: 20px;
  right: 20px;
  background: rgba(10, 12, 22, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--color-border);
  border-radius: 0;
  box-shadow: var(--shadow-soft), 0 0 20px rgba(0, 246, 255, 0.2);
  z-index: 100;
  max-height: 200px; /* Fixed height limit rather than percentage-based */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  clip-path: polygon(
    0 0,
    100% 0,
    100% calc(100% - 15px),
    calc(100% - 15px) 100%,
    0 100%
  );
}

.dialogue-ticker::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--color-accent-primary), transparent, var(--color-accent-primary));
  opacity: 0.7;
}

.dialogue-ticker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
  background-color: rgba(0, 0, 0, 0.2);
}

.dialogue-ticker-title {
  font-size: 0.9rem;
  font-family: var(--font-display);
  color: var(--color-accent-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
  text-shadow: 0 0 5px var(--color-accent-primary);
}

.dialogue-ticker-close {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.dialogue-ticker-close:hover {
  color: var(--color-accent-secondary);
  transform: scale(1.1);
}

.dialogue-messages {
  flex: 1;
  overflow-y: auto;
  max-height: 160px; /* Fixed height instead of percentage-based (200px dialog - 40px header) */
}

/* Animation for the dialogue ticker */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>