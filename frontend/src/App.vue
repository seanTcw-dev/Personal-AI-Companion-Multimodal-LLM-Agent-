<script setup>
import { onMounted } from 'vue';
import { initializeWebSocket } from './services/websocketInit';

// Initialize the WebSocket connection when the app starts
// Optimization: We might want to move this to only init when entering /chat
// But for now, keeping it here ensures connection is ready
onMounted(() => {
  // Optional: check if user is logged in before connecting
  // initializeWebSocket();
});
</script>

<template>
  <router-view />
</template>

<style>
/* Import cyberpunk/anime style fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;800;900&family=Exo+2:wght@300;400;600&family=Rajdhani:wght@400;500;700&display=swap');

/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  font-family: 'Exo 2', 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow: hidden;
}
</style>
