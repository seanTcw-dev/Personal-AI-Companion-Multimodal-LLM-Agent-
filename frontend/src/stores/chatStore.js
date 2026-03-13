import { defineStore } from 'pinia';

/**
 * Chat Store
 * Manages the state of the chat messages and character emotion
 */
export const useChatStore = defineStore('chat', {
  // State
  state: () => ({
    messages: [],
    currentEmotion: 'neutral', // Default emotion
    aiStatus: '',     // Current AI status text (e.g. "Thinking...", "Calling tool...")
    aiStatusActive: false,  // Whether AI is currently processing
    isLocalRequest: false  // True only when THIS window initiated the AI request (not Desktop Pet)
  }),

  // Actions
  actions: {
    /**
     * Add a message to the chat
     * @param {object} message - Message object with text, sender, and optional audio_url
     */
    addMessage(message) {
      // Skip adding hidden messages to the UI
      if (message.hidden) {
        console.log('📝 Hidden message (not shown in UI)');
        return;
      }

      // CRITICAL: Prevent duplicate AI streaming messages
      // If we're adding a new AI streaming message, check if the last message is already an AI streaming message
      if (message.sender === 'ai' && message.streaming) {
        const lastMsg = this.messages[this.messages.length - 1];
        if (lastMsg && lastMsg.sender === 'ai' && lastMsg.streaming) {
          console.log('⚠️ Skipping duplicate AI streaming message (last message is already AI streaming)');
          return;
        }
      }

      this.messages.push({
        id: Date.now(),
        text: message.text,
        sender: message.sender,
        audio_url: message.audio_url || null,
        timestamp: new Date(),
        streaming: message.streaming || false
      });
    },

    /**
     * Send a message - this action will be called by ChatInput component
     * @param {string} text - The message text to send
     */
    sendMessage(text) {
      // First add the message to the chat store
      this.addMessage({
        text: text,
        sender: 'user'
      });

      // The actual WebSocket sending will be handled by the ChatInput component
      // This action is mainly for future expansion, like adding additional
      // processing or side effects when sending messages
    },

    /**
     * Set the current emotion for the character
     * @param {string} emotion - The emotion to set
     */
    setEmotion(emotion) {
      this.currentEmotion = emotion;
    },

    /**
     * Clear all messages from the chat
     */
    clearMessages() {
      this.messages = [];
    },

    /**
     * Set the AI processing status
     * @param {string} status - Status key (thinking, tool_calling, generating, voice, idle)
     * @param {string} detail - Human-readable detail text
     */
    setAiStatus(status, detail) {
      if (status === 'idle' || !status) {
        this.aiStatus = '';
        this.aiStatusActive = false;
        this.isLocalRequest = false;
      } else {
        this.aiStatus = detail || status;
        this.aiStatusActive = true;
        // Note: isLocalRequest is set separately by sendMessage, not here
        // This allows status updates from Desktop Pet to NOT show in Web UI
      }
    },

    /**
     * Mark that this window is the one that initiated the current AI request
     */
    setLocalRequest(value) {
      this.isLocalRequest = value;
    }
  }
});