/**
 * WebSocket Service
 * Manages the WebSocket connection to the backend server for real-time communication
 */

import { useChatStore } from '../stores/chatStore';
import { useConversationStore } from '../stores/conversationStore';
import { lipSyncService } from './lipSyncService';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
    this.backendUrl = 'ws://localhost:8000'; // Default backend URL
    this.currentAudio = null; // Track current playing audio
    this.audioQueue = []; // Queue for streaming audio playback
    this.isPlayingQueue = false; // Flag to track if queue is being processed
    this.streamingMessageId = null; // Track the current streaming message ID
    this.accumulatedText = ''; // Accumulate text during streaming
    this._currentUserId = null; // Store userId for reconnection
    this._conversationIdToRestore = null; // Conversation ID to restore after stop-reconnect
  }

  /**
   * Terminate the current AI response
   * Disconnects and reconnects the WebSocket to cancel processing
   */
  terminateResponse() {
    console.log('🛑 Terminating AI response...');
    const chatStore = useChatStore();
    chatStore.setAiStatus('idle', '');

    // Clear audio queue
    this.audioQueue = [];
    this.isPlayingQueue = false;
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }

    // Reset streaming state
    this.streamingMessageId = null;
    this.accumulatedText = '';

    // Save active conversation ID so we can restore it after reconnect
    const conversationStore = useConversationStore();
    this._conversationIdToRestore = conversationStore.activeConversationId;
    console.log('💾 Saving conversation to restore:', this._conversationIdToRestore);

    // Reconnect websocket to cancel backend processing
    if (this.socket) {
      const userId = this._currentUserId;
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
      // Reconnect after a brief delay
      setTimeout(() => {
        this.connect(userId);
      }, 300);
    }
  }

  /**
   * Connect to the WebSocket server
   * @param {string} userId - The user ID for this connection
   */
  connect(userId) {
    // Check if already connected OR connecting
    if (this.isConnected) {
      console.log('✅ WebSocket already connected');
      return;
    }

    // CRITICAL: Also check if socket exists and is CONNECTING or OPEN
    // This prevents duplicate connections when called multiple times before onopen fires
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
      console.log('⏳ WebSocket already connecting or open, skipping duplicate connect()');
      return;
    }

    try {
      const url = `${this.backendUrl}/ws/chat/${userId}`;
      console.log(`🔌 Connecting to WebSocket: ${url}`);
      this._currentUserId = userId;
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log('✅ WebSocket connection established');
        this.isConnected = true;
        this.reconnectAttempts = 0;

        // Restore conversation if reconnecting after stop
        if (this._conversationIdToRestore) {
          console.log('🔄 Restoring conversation after stop:', this._conversationIdToRestore);
          this.socket.send(JSON.stringify({
            type: 'restore_conversation',
            conversation_id: this._conversationIdToRestore
          }));
          this._conversationIdToRestore = null;
        }
      };

      this.socket.onmessage = (event) => {
        console.log('📥 Received message:', event.data);
        this.handleMessage(event.data);
      };

      this.socket.onclose = (event) => {
        console.log('❌ WebSocket connection closed', event.code, event.reason);
        this.isConnected = false;

        // Attempt to reconnect
        this.attemptReconnect(userId);
      };

      this.socket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        console.error('Error details:', {
          readyState: this.socket?.readyState,
          url: url
        });
      };
    } catch (error) {
      console.error('❌ Failed to connect to WebSocket server:', error);
    }
  }

  /**
   * Send a message through the WebSocket
   * @param {object} message - Message object to send
   */
  sendMessage(message) {
    if (!this.isConnected || !this.socket) {
      console.error('Cannot send message: WebSocket not connected');
      return;
    }

    try {
      // Set AI status to processing immediately
      const chatStore = useChatStore();
      chatStore.setLocalRequest(true); // Mark that THIS window initiated the request
      chatStore.setAiStatus('thinking', 'Processing your message...');

      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }

  /**
   * Handle incoming messages from the WebSocket
   * @param {string} data - The raw message data
   */
  handleMessage(data) {
    try {
      // Parse the message data
      const parsedData = JSON.parse(data);

      // Access the chat store
      const chatStore = useChatStore();
      const conversationStore = useConversationStore();

      // Check if this is a status update message
      if (parsedData.type === 'status') {
        console.log('📊 AI Status update:', parsedData.status, parsedData.detail);
        chatStore.setAiStatus(parsedData.status, parsedData.detail);
        return;
      }

      // Handle echoed user messages from other connections (e.g. desktop pet → web)
      if (parsedData.type === 'user_message_echo') {
        // Prevent duplicate if we just sent this message yourself
        // Check last 5 messages to be safe (allow for some async race conditions)
        const recentMessages = chatStore.messages.slice(-5);
        const isDuplicate = recentMessages.some(msg =>
          msg.sender === 'user' && msg.text === parsedData.text
        );

        if (isDuplicate) {
          console.log('🔄 Ignoring duplicate echo for own message:', parsedData.text);
          return;
        }

        // If the echo has a conversation_id that differs from the active one,
        // it came from Desktop Pet in a different conversation — don't show it here
        if (parsedData.conversation_id && parsedData.conversation_id !== conversationStore.activeConversationId) {
          console.log('🚫 Ignoring echo from different conversation (Desktop Pet):', parsedData.conversation_id);
          return;
        }

        // Fallback: if conversation_id is null (new Desktop Pet conversation not yet created)
        // and this window didn't initiate the request, it must be from Desktop Pet — ignore it
        if (!parsedData.conversation_id && !chatStore.isLocalRequest) {
          console.log('🚫 Ignoring echo from Desktop Pet (no conversation_id, not local request)');
          return;
        }

        console.log('📨 User message echo from another connection:', parsedData.text);
        chatStore.addMessage({ text: parsedData.text, sender: 'user' });
        return;
      }

      // Handle conversation created notification (soft sync)
      if (parsedData.type === 'conversation_created') {
        console.log('📢 Received conversation_created event:', parsedData);

        // Dispatch custom event for UI components to show notification
        window.dispatchEvent(new CustomEvent('conversation:created', {
          detail: {
            conversationId: parsedData.conversation_id,
            conversationTitle: parsedData.conversation_title,
            source: parsedData.source
          }
        }));

        // Reload conversations list to include the new one
        conversationStore.loadConversations();
        return;
      }

      // Check if this is a streaming message
      if (parsedData.streaming) {
        this.handleStreamingMessage(parsedData, chatStore, conversationStore);
        return;
      }

      // Regular (non-streaming) message handling
      // Only show AI response if it belongs to the currently active conversation
      const msgConvId = parsedData.conversation_id;
      if (msgConvId && msgConvId !== conversationStore.activeConversationId) {
        console.log('🚫 Ignoring AI response from different conversation (Desktop Pet):', msgConvId);
        // Still update conversation metadata (title, list) but don't show the message
        if (!conversationStore.activeConversationId) {
          // Web UI is in "New Chat" mode — this shouldn't happen for Desktop Pet messages
        }
        return;
      }

      // Add the message to the chat store (AI response always shows)
      chatStore.addMessage({
        text: parsedData.text,
        sender: 'ai',
        audio_url: parsedData.audio_url // Include audio URL if present
      });

      // Update the character's emotion if provided
      if (parsedData.emotion) {
        chatStore.setEmotion(parsedData.emotion);
      }

      // Handle Conversation Metadata Updates (Auto-naming / Creation)
      if (parsedData.conversation_id) {
        // If we are currently in "New Chat" (no ID) and backend sent an ID
        if (!conversationStore.activeConversationId) {
          console.log('✨ Auto-switching to created conversation:', parsedData.conversation_id);
          // We need to reload the list to get the full conversation object
          conversationStore.loadConversations().then(() => {
            conversationStore.switchConversation(parsedData.conversation_id);
          });
        }
        // If we are already in a conversation but the title changed
        else if (conversationStore.activeConversationId === parsedData.conversation_id) {
          if (parsedData.conversation_title) {
            const currentConv = conversationStore.activeConversation;
            if (currentConv && currentConv.title !== parsedData.conversation_title) {
              console.log('📝 Updating conversation title:', parsedData.conversation_title);
              currentConv.title = parsedData.conversation_title;
            }
          }
        }
      }

      // 🎵 AUTO-PLAY AUDIO if audio_url is provided
      if (parsedData.audio_url) {
        console.log('🔊 Playing voice audio:', parsedData.audio_url);
        this.playAudio(parsedData.audio_url);

        // Dispatch event for character speaking (for animation sync)
        window.dispatchEvent(new CustomEvent('character:speak', {
          detail: {
            text: parsedData.text,
            audioUrl: parsedData.audio_url
          }
        }));
      }
    } catch (error) {
      console.error('❌ Error processing WebSocket message:', error);
      console.error('📄 Problematic data:', data);

      // DO NOT auto-add as AI message if parsing fails - this causes ghost messages!
      // Only log the error so we can debug why we received non-JSON data
      /*
      const chatStore = useChatStore();
      chatStore.addMessage({
        text: data,
        sender: 'ai'
      });
      */
    }
  }

  /**
   * Handle streaming messages (sentence-by-sentence)
   * @param {object} parsedData - Parsed message data
   * @param {object} chatStore - Chat store instance
   * @param {object} conversationStore - Conversation store instance
   */
  handleStreamingMessage(parsedData, chatStore, conversationStore) {
    console.log('🌊 Streaming message received:', parsedData);
    console.log('🔍 is_final:', parsedData.is_final, 'sentence:', parsedData.sentence);

    // Check if this message belongs to the currently active conversation.
    // If the backend sends a conversation_id that differs from what the Web UI is viewing,
    // it means the Desktop Pet sent this message in a different conversation — ignore it in UI.
    // (The message is already saved to the JSON file by the backend.)
    const msgConvId = parsedData.conversation_id;
    const isForActiveConversation = !msgConvId || msgConvId === conversationStore.activeConversationId;

    if (!isForActiveConversation) {
      console.log('🚫 Streaming message from different conversation (Desktop Pet), skipping UI update:', msgConvId);
      // Still reload conversations list so sidebar stays up to date
      if (parsedData.is_final) {
        conversationStore.loadConversations();
        // Reset streaming state so next local message starts fresh
        this.streamingMessageId = null;
        this.accumulatedText = '';
      }
      return;
    }

    if (parsedData.is_final) {
      // Final message - update metadata
      console.log('✅ Streaming complete. Final text:', parsedData.text);

      // Update accumulated text in the last message
      if (this.streamingMessageId !== null) {
        const messages = chatStore.messages;
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.sender === 'ai') {
          lastMessage.text = parsedData.text;
        }
      }

      // Update conversation metadata
      if (parsedData.conversation_id) {
        if (!conversationStore.activeConversationId) {
          console.log('✨ Auto-switching to created conversation:', parsedData.conversation_id);
          conversationStore.loadConversations().then(() => {
            conversationStore.switchConversation(parsedData.conversation_id);
          });
        } else if (conversationStore.activeConversationId === parsedData.conversation_id) {
          if (parsedData.conversation_title) {
            const currentConv = conversationStore.activeConversation;
            if (currentConv && currentConv.title !== parsedData.conversation_title) {
              console.log('📝 Updating conversation title:', parsedData.conversation_title);
              currentConv.title = parsedData.conversation_title;
            }
          }
        }
      }

      // Reset streaming state
      this.streamingMessageId = null;
      this.accumulatedText = '';
    } else {
      // Sentence fragment - backend sends sentence text in "text" field
      const sentence = parsedData.text || parsedData.sentence || '';
      const sentenceIndex = parsedData.sentence_index || 1;

      // For non-final messages, skip if sentence is empty
      if ((!sentence || sentence.trim() === '') && !parsedData.is_final) {
        console.log(`⚠️ Received empty sentence ${sentenceIndex} (not final), skipping`);
        return;
      }

      // Only log if we have actual sentence content
      if (sentence && sentence.trim()) {
        console.log(`📝 Sentence ${sentenceIndex}: ${sentence.substring(0, 50)}...`);

        // Accumulate text
        this.accumulatedText += sentence + ' ';
      }

      // If this is the first sentence, create a new message
      if (sentenceIndex === 1 && sentence && sentence.trim()) {
        this.streamingMessageId = Date.now();
        chatStore.addMessage({
          text: this.accumulatedText,
          sender: 'ai',
          streaming: true
        });
      } else if (sentence && sentence.trim()) {
        // Update the existing streaming message
        const messages = chatStore.messages;
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.sender === 'ai') {
          lastMessage.text = this.accumulatedText;
        }
      }

      // Update emotion
      if (parsedData.emotion) {
        chatStore.setEmotion(parsedData.emotion);
      }

      // Queue audio for playback (only if we have a sentence with audio)
      if (sentence && sentence.trim() && parsedData.audio_url) {
        console.log(`🎵 Queueing audio ${sentenceIndex}: ${parsedData.audio_url}`);
        this.audioQueue.push({
          url: parsedData.audio_url,
          text: sentence,
          index: sentenceIndex
        });

        // Start playing queue if not already playing
        if (!this.isPlayingQueue) {
          this.playAudioQueue();
        }

        // Dispatch event for character speaking
        window.dispatchEvent(new CustomEvent('character:speak', {
          detail: {
            text: sentence,
            audioUrl: parsedData.audio_url
          }
        }));
      }
    }
  }

  /**
   * Play audio queue sequentially
   */
  async playAudioQueue() {
    if (this.isPlayingQueue || this.audioQueue.length === 0) {
      return;
    }

    this.isPlayingQueue = true;
    console.log(`🎵 Starting audio queue playback (${this.audioQueue.length} items)`);

    while (this.audioQueue.length > 0) {
      const audioItem = this.audioQueue.shift();
      console.log(`▶️ Playing audio ${audioItem.index}: ${audioItem.text.substring(0, 30)}...`);

      try {
        await this.playAudioPromise(audioItem.url);
      } catch (error) {
        console.error('❌ Error playing queued audio:', error);
      }
    }

    this.isPlayingQueue = false;
    console.log('✅ Audio queue playback complete');
  }

  /**
   * Play audio and return a promise that resolves when playback ends
   * @param {string} audioUrl - URL to the audio file
   * @returns {Promise} Promise that resolves when audio finishes
   */
  playAudioPromise(audioUrl) {
    return new Promise((resolve, reject) => {
      try {
        // Stop any currently playing audio
        if (this.currentAudio) {
          this.currentAudio.pause();
          this.currentAudio = null;
        }

        // Create full URL
        const fullUrl = `http://localhost:8000${audioUrl}`;

        // Create audio element
        const audio = new Audio(fullUrl);
        audio.crossOrigin = 'anonymous'; // Required for Web Audio API
        this.currentAudio = audio;

        // Connect to lip sync analyser
        lipSyncService.connectAudio(audio);

        audio.addEventListener('loadeddata', () => {
          console.log('✅ Audio loaded');
        });

        audio.addEventListener('play', () => {
          window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: true } }));
        });

        audio.addEventListener('error', (e) => {
          console.error('❌ Error loading audio:', e);
          this.currentAudio = null;
          window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
          reject(e);
        });

        audio.addEventListener('ended', () => {
          console.log('✅ Audio finished');
          this.currentAudio = null;
          window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
          resolve();
        });

        // Play the audio
        audio.play().catch(error => {
          console.error('❌ Error playing audio:', error);
          this.currentAudio = null;
          window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
          reject(error);
        });

      } catch (error) {
        console.error('❌ Error in playAudioPromise:', error);
        this.currentAudio = null;
        window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
        reject(error);
      }
    });
  }

  /**
   * Play audio from URL
   * @param {string} audioUrl - URL to the audio file
   */
  playAudio(audioUrl) {
    try {
      // Stop any currently playing audio
      if (this.currentAudio) {
        this.currentAudio.pause();
        this.currentAudio = null;
      }

      // Create full URL (backend is on port 8000)
      const fullUrl = `http://localhost:8000${audioUrl}`;

      // Create and play audio
      const audio = new Audio(fullUrl);
      audio.crossOrigin = 'anonymous'; // Required for Web Audio API
      this.currentAudio = audio;

      // Connect to lip sync analyser
      lipSyncService.connectAudio(audio);

      audio.addEventListener('loadeddata', () => {
        console.log('✅ Audio loaded, playing...');
      });

      audio.addEventListener('play', () => {
        console.log('🔊 AI started speaking');
        // Emit event that AI is speaking
        window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: true } }));
      });

      audio.addEventListener('error', (e) => {
        console.error('❌ Error loading audio:', e);
        this.currentAudio = null;
        window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
      });

      audio.addEventListener('ended', () => {
        console.log('✅ Audio playback complete');
        this.currentAudio = null;
        // Emit event that AI stopped speaking
        window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
      });

      audio.addEventListener('pause', () => {
        console.log('⏸️ Audio paused');
        this.currentAudio = null;
        window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
      });

      // Play the audio
      audio.play().catch(error => {
        console.error('❌ Error playing audio:', error);
        console.log('💡 Note: Browser may require user interaction before playing audio');
        this.currentAudio = null;
        window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
      });

    } catch (error) {
      console.error('❌ Error in playAudio:', error);
      this.currentAudio = null;
      window.dispatchEvent(new CustomEvent('ai-speaking', { detail: { speaking: false } }));
    }
  }

  /**
   * Attempt to reconnect to the WebSocket server
   * @param {string} userId - The user ID for this connection
   */
  attemptReconnect(userId) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`Attempting to reconnect in ${delay / 1000} seconds...`);

    clearTimeout(this.reconnectTimeout);
    this.reconnectTimeout = setTimeout(() => {
      this.connect(userId);
    }, delay);
  }

  /**
   * Close the WebSocket connection
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
      clearTimeout(this.reconnectTimeout);
    }
  }
}

// Create and export a singleton instance
export const websocketService = new WebSocketService();