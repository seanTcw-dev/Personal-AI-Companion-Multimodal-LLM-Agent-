import { websocketService } from './websocket';

/**
 * Initialize WebSocket connection
 * This should be called when the app starts
 */
export function initializeWebSocket() {
  // Get authenticated user ID from localStorage
  const userDataStr = localStorage.getItem('user');
  let userId = 'user_default'; // Fallback for guest users

  if (userDataStr) {
    try {
      const userData = JSON.parse(userDataStr);
      // Use Google sub (user ID) if available
      if (userData.sub) {
        userId = userData.sub;
        console.log(`🔐 Using authenticated user ID: ${userId}`);
      }
    } catch (e) {
      console.warn('Failed to parse user data, using default user ID');
    }
  } else {
    console.log('📝 No user data found, using guest user ID');
  }

  console.log(`🔌 Initializing WebSocket for user: ${userId}`);

  console.log(`🚀 Initializing WebSocket with user ID: ${userId}`);

  // Connect to the WebSocket server
  websocketService.connect(userId);
}