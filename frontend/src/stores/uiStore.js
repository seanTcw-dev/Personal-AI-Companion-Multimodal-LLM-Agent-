import { defineStore } from 'pinia';

/**
 * UI Store
 * Manages UI state for the application
 */
export const useUIStore = defineStore('ui', {
  // State
  state: () => ({
    isDialogueTickerVisible: false
  }),
  
  // Actions
  actions: {
    /**
     * Set the visibility of the dialogue ticker
     * @param {boolean} visible - Whether the dialogue ticker should be visible
     */
    setDialogueTickerVisibility(visible) {
      this.isDialogueTickerVisible = visible;
    }
  }
});