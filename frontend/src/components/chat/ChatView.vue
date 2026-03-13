<template>
  <div class="chat-view">
    <div class="messages-container">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.sender">
        <div class="message-content">
          {{ message.text }}
        </div>
      </div>
    </div>
    <div class="input-container">
      <input 
        v-model="newMessage" 
        @keyup.enter="sendMessage"
        placeholder="Type your message..." 
        class="message-input" 
      />
      <button @click="sendMessage" class="send-button">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useChatStore } from '../../stores/chatStore';
import { websocketService } from '../../services/websocket';

const chatStore = useChatStore();
const { messages } = chatStore;
const newMessage = ref('');

const sendMessage = () => {
  if (newMessage.value.trim()) {
    // Add the user message to the chat store
    chatStore.addMessage({
      text: newMessage.value,
      sender: 'user'
    });
    
    // Send the message through the WebSocket service
    websocketService.sendMessage({
      text: newMessage.value
    });
    
    // Clear the input
    newMessage.value = '';
  }
};

onMounted(() => {
  // Connect to the WebSocket when the component is mounted
  websocketService.connect('user-1'); // Using a default user ID
});
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f5f5f5;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 1rem;
  max-width: 80%;
  padding: 0.75rem;
  border-radius: 1rem;
}

.message.user {
  align-self: flex-end;
  background-color: #3b82f6;
  color: white;
}

.message.ai {
  align-self: flex-start;
  background-color: #e2e8f0;
  color: #334155;
}

.input-container {
  display: flex;
  padding: 1rem;
  background-color: #fff;
  border-top: 1px solid #e2e8f0;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  margin-right: 0.5rem;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

.send-button:hover {
  background-color: #2563eb;
}
</style>