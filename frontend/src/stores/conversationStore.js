import { defineStore } from 'pinia';

/**
 * Conversation Store
 * Manages multiple chat conversations and active conversation state
 */
export const useConversationStore = defineStore('conversation', {
    // State
    state: () => ({
        conversations: [],           // List of all conversations
        activeConversationId: null,  // Currently active conversation ID
        loading: false,              // Loading state
        error: null,                 // Error message
        currentUserId: null          // Authenticated user ID
    }),

    // Getters
    getters: {
        /**
         * Get the active conversation object
         */
        activeConversation(state) {
            if (!state.activeConversationId) return null;
            return state.conversations.find(c => c.id === state.activeConversationId);
        },

        /**
         * Get conversations sorted by update time (newest first)
         */
        sortedConversations(state) {
            return [...state.conversations].sort((a, b) => {
                return new Date(b.updated_at) - new Date(a.updated_at);
            });
        },

        /**
         * Get current user ID (helper)
         */
        userId(state) {
            if (state.currentUserId) return state.currentUserId;

            // Try to get from localStorage
            const userDataStr = localStorage.getItem('user');
            if (userDataStr) {
                try {
                    const userData = JSON.parse(userDataStr);
                    if (userData.sub) return userData.sub;
                } catch (e) {
                    console.warn('Failed to parse user data');
                }
            }
            return 'user_default';
        }
    },

    // Actions
    actions: {
        /**
         * Initialize store (set user ID)
         */
        initialize() {
            const userDataStr = localStorage.getItem('user');
            if (userDataStr) {
                try {
                    const userData = JSON.parse(userDataStr);
                    if (userData.sub) {
                        this.currentUserId = userData.sub;
                        console.log('👤 ConversationStore initialized with User ID:', this.currentUserId);
                    }
                } catch (e) {
                    console.warn('Failed to parse user data');
                }
            }
        },

        /**
         * Load all conversations from backend
         */
        async loadConversations(userId = null) {
            const targetUserId = userId || this.userId;
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(`http://localhost:8000/api/conversations?user_id=${targetUserId}`);
                const data = await response.json();

                if (data.success) {
                    this.conversations = data.conversations;
                }
            } catch (error) {
                console.error('Failed to load conversations:', error);
                this.error = 'Failed to load conversations';
            } finally {
                this.loading = false;
            }
        },

        /**
         * Create a new conversation
         */
        async createConversation(title = 'New Chat', userId = null) {
            const targetUserId = userId || this.userId;
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch('http://localhost:8000/api/conversations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: targetUserId,
                        title: title
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Add to conversations list
                    const newConv = {
                        id: data.conversation.id,
                        title: data.conversation.title,
                        created_at: data.conversation.created_at,
                        updated_at: data.conversation.updated_at,
                        message_count: 0
                    };

                    this.conversations.unshift(newConv);

                    // Set as active conversation
                    this.activeConversationId = newConv.id;

                    console.log('✅ Created new conversation:', newConv.id);
                    return newConv;
                }
            } catch (error) {
                console.error('Failed to create conversation:', error);
                this.error = 'Failed to create conversation';
            } finally {
                this.loading = false;
            }
        },

        /**
         * Switch to a different conversation
         */
        switchConversation(conversationId) {
            this.activeConversationId = conversationId;
            console.log('🔄 Switched to conversation:', conversationId);
        },

        /**
         * Delete a conversation
         */
        async deleteConversation(conversationId, userId = null) {
            const targetUserId = userId || this.userId;
            try {
                const response = await fetch(`http://localhost:8000/api/conversations/${conversationId}?user_id=${targetUserId}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (data.success) {
                    // Remove from local state
                    this.conversations = this.conversations.filter(c => c.id !== conversationId);

                    // If deleted conversation was active, switch to first available
                    if (this.activeConversationId === conversationId) {
                        this.activeConversationId = this.conversations.length > 0 ? this.conversations[0].id : null;
                    }

                    console.log('🗑️ Deleted conversation:', conversationId);
                }
            } catch (error) {
                console.error('Failed to delete conversation:', error);
                this.error = 'Failed to delete conversation';
            }
        },

        /**
         * Rename a conversation
         */
        async renameConversation(conversationId, newTitle, userId = null) {
            const targetUserId = userId || this.userId;
            try {
                const response = await fetch(`http://localhost:8000/api/conversations/${conversationId}?user_id=${targetUserId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title: newTitle
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Update local state
                    const conv = this.conversations.find(c => c.id === conversationId);
                    if (conv) {
                        conv.title = newTitle;
                        conv.updated_at = new Date().toISOString();
                    }
                    console.log('📝 Renamed conversation:', conversationId, '->', newTitle);
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Failed to rename conversation:', error);
                this.error = 'Failed to rename conversation';
                return false;
            }
        },

        /**
         * Update conversation metadata (message count, updated_at)
         */
        updateConversationMetadata(conversationId) {
            const conv = this.conversations.find(c => c.id === conversationId);
            if (conv) {
                conv.message_count = (conv.message_count || 0) + 1;
                conv.updated_at = new Date().toISOString();
            }
        }
    }
});
