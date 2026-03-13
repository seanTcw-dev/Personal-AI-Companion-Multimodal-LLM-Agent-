<template>
  <div class="chat-sidebar">
    <!-- 1. Header with Logo -->
    <div class="sidebar-brand">
      <div class="brand-ring">
        <span class="brand-v">V</span>
      </div>
      <h1 class="brand-title"><span class="brand-name">Virtu<span class="ai-glow">A<span class="serif-i">I</span></span></span> Companion</h1>
    </div>

    <!-- 2. Action Buttons Area -->
    <div class="sidebar-actions">
      <!-- New Chat Button -->
      <button class="action-btn primary new-chat-btn" @click="createNewChat">
        <span class="icon">+</span>
        <span>New Chat</span>
      </button>

      <!-- Search Button (Visual only for now) -->
      <button class="action-btn secondary search-btn">
        <span class="icon">🔍</span>
        <span>Search</span>
      </button>

      <!-- Email Client Button -->
      <button class="action-btn secondary email-btn" @click="openEmailClient">
        <span class="icon">📧</span>
        <span>Email Client</span>
      </button>

      <!-- History Toggle Button -->
      <button class="action-btn secondary history-btn" @click="toggleHistory" :class="{ active: isHistoryVisible }">
        <span class="icon">📜</span>
        <span>Open Conversation History</span>
      </button>
    </div>

    <!-- 3. Chat History List -->
    <div class="history-section">
      <div class="section-label">CHAT HISTORY</div>
      
      <div class="conversations-list">
        <div
          v-for="conv in sortedConversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ active: conv.id === activeConversationId }"
          @click="switchToConversation(conv.id)"
        >
          <div class="item-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div class="item-content">
            <div class="item-title">{{ conv.title }}</div>
            <div class="item-meta">{{ formatTime(conv.updated_at) }}</div>
          </div>
          
          <button
            class="delete-btn"
            @click.stop="deleteConv(conv.id)"
            title="Delete"
          >
            🗑️
          </button>
        </div>

        <!-- Empty state -->
        <div v-if="sortedConversations.length === 0" class="empty-state">
          <p>No chat history</p>
        </div>
      </div>
    </div>

    <!-- 4. User Profile Section -->
    <div class="user-profile-section">
      <div class="user-avatar-wrapper" @click="toggleSettingsMenu">
        <img 
          :src="userAvatar" 
          alt="User Avatar" 
          class="user-avatar clickable"
          :class="{ active: showSettingsMenu }"
        />
        <span class="status-dot"></span>
      </div>
      <div class="user-info" @click="toggleSettingsMenu">
        <div class="user-name clickable">{{ userName }}</div>
      </div>
      <button class="icon-btn desktop-mode-trigger" @click.stop="launchDesktopPet" title="Desktop Mode">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
          <line x1="8" y1="21" x2="16" y2="21"></line>
          <line x1="12" y1="17" x2="12" y2="21"></line>
        </svg>
      </button>
      <button class="icon-btn sign-out-icon" @click="handleSignOut" title="Sign Out">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
      </button>
      
      <!-- Settings Dropdown Menu -->
      <transition name="slide-fade">
        <div v-if="showSettingsMenu" class="settings-dropdown">
          <div class="dropdown-header">
            <h3>SETTINGS</h3>
          </div>
          
          <div class="dropdown-item" @click="openUserProfile">
            <div class="item-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <div class="item-text">
              <div class="item-title">User Profile</div>
              <div class="item-desc">Manage your account</div>
            </div>
          </div>
          
          <div class="dropdown-item" @click="openVoiceSettings">
            <div class="item-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
            </div>
            <div class="item-text">
              <div class="item-title">Voice Settings</div>
              <div class="item-desc">Configure voice & audio</div>
            </div>
          </div>
          
          <div class="dropdown-item" @click="open3DModelSettings">
            <div class="item-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <div class="item-text">
              <div class="item-title">3D Model</div>
              <div class="item-desc">Customize character</div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useConversationStore } from '../../stores/conversationStore';
import { useChatStore } from '../../stores/chatStore';
import { useUIStore } from '../../stores/uiStore';
// import { googleLogout } from 'vue3-google-login'; // Enable if using real auth

const router = useRouter();
const conversationStore = useConversationStore();
const chatStore = useChatStore();
const uiStore = useUIStore();

// User profile data
const userName = ref('Sean');
const userAvatar = ref('https://api.dicebear.com/7.x/avataaars/svg?seed=Sean');
const showSettingsMenu = ref(false);

// Load user data from localStorage (if logged in with Google)
const loadUserData = () => {
  try {
    const userData = localStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      userName.value = user.name || 'Sean';
      userAvatar.value = user.picture || 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sean';
    }
  } catch (error) {
    console.error('Failed to load user data:', error);
  }
};

// Toggle settings menu
const toggleSettingsMenu = () => {
  showSettingsMenu.value = !showSettingsMenu.value;
};

// Close settings menu when clicking outside
const handleClickOutside = (event) => {
  const profileSection = document.querySelector('.user-profile-section');
  if (profileSection && !profileSection.contains(event.target)) {
    showSettingsMenu.value = false;
  }
};

// Settings menu actions
const openUserProfile = () => {
  console.log('📝 Opening User Profile settings...');
  showSettingsMenu.value = false;
  router.push('/settings/profile');
};

const openVoiceSettings = () => {
  console.log('🎤 Opening Voice settings...');
  showSettingsMenu.value = false;
  router.push('/settings/voice');
};

const openEmailClient = () => {
  console.log('📧 Opening Email Client...');
  router.push('/email');
};

const open3DModelSettings = () => {
  console.log('🎭 Opening 3D Model settings...');
  showSettingsMenu.value = false;
  router.push('/settings/model');
};

const launchDesktopPet = async () => {
    console.log('🖥️ Launching Desktop Mode...');
    try {
        const response = await fetch('http://localhost:8000/api/system/desktop-mode', {
            method: 'POST'
        });
        
        if (response.ok) {
            console.log('✅ Desktop mode launched successfully');
            showSettingsMenu.value = false;
        } else {
            console.error('❌ Failed to launch desktop mode');
        }
    } catch (error) {
        console.error('❌ Error launching desktop mode:', error);
    }
};

const sortedConversations = computed(() => {
  const convs = conversationStore.sortedConversations;

  console.log('📋 Sorted conversations:', convs.length, convs);
  return convs;
});
const activeConversationId = computed(() => conversationStore.activeConversationId);

// Load conversations on mount
onMounted(async () => {
  console.log('🎬 ChatSidebar mounted, loading conversations...');
  
  // Load user data
  loadUserData();
  
  // Add click outside listener
  document.addEventListener('click', handleClickOutside);
  
  await conversationStore.loadConversations();
  console.log('✅ Conversations loaded:', conversationStore.conversations.length);
  
  // If there are conversations, make sure the active one's messages are loaded
  if (conversationStore.activeConversationId) {
    const activeId = conversationStore.activeConversationId;
    console.log('🔄 Loading messages for active conversation:', activeId);
    
    // Switch to it (this loads messages)
    await switchToConversation(activeId);
  } else {
    // No active conversation selected - Create a fresh "New Chat" state in UI without backend call yet
    console.log('🆕 Starting with fresh UI state');
    chatStore.clearMessages();
  }
});

// Cleanup on unmount
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Create new chat
const createNewChat = async () => {
  // Create new conversation in backend
  const newConv = await conversationStore.createConversation('New Chat');
  
  if (newConv) {
    // Clear messages in UI
    chatStore.clearMessages();
    
    // Activate this conversation in backend
    try {
      const userId = conversationStore.userId;
      await fetch(`http://localhost:8000/api/conversations/${newConv.id}/activate?user_id=${userId}`, {
        method: 'POST'
      });
      console.log('✅ New chat created and activated:', newConv.id);
    } catch (error) {
      console.error('Failed to activate new conversation:', error);
    }
  }
};

// Switch to a conversation
const switchToConversation = async (convId) => {
  console.log('🔄 Switching to conversation:', convId);
  conversationStore.switchConversation(convId);
  
  // Auto-open conversation history
  uiStore.setDialogueTickerVisibility(true);
  
  // Notify backend to set this as active conversation
  const userId = conversationStore.userId;
  try {
    await fetch(`http://localhost:8000/api/conversations/${convId}/activate?user_id=${userId}`, {
      method: 'POST'
    });
    console.log('✅ Backend activated conversation:', convId);
  } catch (error) {
    console.error('Failed to activate conversation in backend:', error);
  }
  
  // Load conversation messages
  try {
    const response = await fetch(`http://localhost:8000/api/conversations/${convId}?user_id=${userId}`);
    const data = await response.json();
    
    console.log('📥 Loaded conversation data:', data);
    
    if (data.success && data.conversation) {
      const messages = data.conversation.messages;
      console.log(`📨 Found ${messages.length} messages in conversation`);
      
      // Clear and load messages into chat store
      chatStore.clearMessages();
      console.log('🗑️ Cleared existing messages');
      
      messages.forEach((msg, index) => {
        console.log(`➕ Adding message ${index + 1}:`, msg.role, msg.content.substring(0, 50));
        chatStore.addMessage({
          text: msg.content,
          sender: msg.role === 'user' ? 'user' : 'ai'
        });
      });
      
      console.log('✅ All messages loaded into chat store');
    }
  } catch (error) {
    console.error('Failed to load conversation:', error);
  }
};

// Delete conversation
const deleteConv = async (convId) => {
  if (confirm('Delete this conversation?')) {
    await conversationStore.deleteConversation(convId);
    chatStore.clearMessages();
  }
};

// Utility function
const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
  
  return date.toLocaleDateString();
};

const isHistoryVisible = computed(() => uiStore.isDialogueTickerVisible);

// Sign Out Handler
const handleSignOut = () => {
  if (confirm('Are you sure you want to sign out?')) {
    console.log('👋 User signing out...');
    
    // 1. Clear localStorage (user data & auth status)
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    
    // 2. Clear chat messages
    chatStore.clearMessages();
    
    // 3. Clear conversation store
    conversationStore.$reset();
    
    // 4. Clear UI state
    uiStore.$reset();
    
    // 5. Google Logout (if using Google auth)
    // googleLogout(); // Uncomment if using real Google auth
    
    console.log('✅ All state cleared');
    
    // 6. Navigate to landing page
    router.push('/');
  }
};

const toggleHistory = () => {
  uiStore.setDialogueTickerVisibility(!uiStore.isDialogueTickerVisible);
};
</script>

<style scoped>
.chat-sidebar {
  width: 280px;
  height: 100%;
  background: #0B0D14; /* Darker background */
  border-right: 1px solid rgba(0, 246, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
  gap: 24px;
}

/* User Profile Section */
.user-profile-section {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 4px;
  margin-top: auto;
  border-radius: 8px;
  background: transparent;
  border: none;
  transition: all 0.3s ease;
  position: relative;
}

.user-profile-section:hover {
  background: rgba(0, 246, 255, 0.02);
}

.clickable {
  cursor: pointer;
}

.user-avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid #00F6FF;
  box-shadow: 
    0 0 8px rgba(0, 246, 255, 0.4),
    0 0 16px rgba(0, 246, 255, 0.2),
    inset 0 0 8px rgba(0, 246, 255, 0.15);
  object-fit: cover;
  filter: brightness(1.1);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  box-shadow: 
    0 0 12px rgba(0, 246, 255, 0.6),
    0 0 24px rgba(0, 246, 255, 0.3),
    inset 0 0 12px rgba(0, 246, 255, 0.25);
  transform: scale(1.05);
}

.user-avatar.active {
  box-shadow: 
    0 0 15px rgba(0, 246, 255, 0.8),
    0 0 30px rgba(0, 246, 255, 0.4),
    inset 0 0 15px rgba(0, 246, 255, 0.3);
  transform: scale(1.08);
}

.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  background: #00F6FF;
  border: 2px solid #0B0D14;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 246, 255, 0.8);
  animation: pulse-status 2s ease-in-out infinite;
}

@keyframes pulse-status {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 8px rgba(0, 246, 255, 0.8);
  }
  50% {
    opacity: 0.6;
    box-shadow: 0 0 4px rgba(0, 246, 255, 0.5);
  }
}

.user-info {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-family: 'Rajdhani', var(--font-body), sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #E8EDFF;
  letter-spacing: 0.3px;
  text-shadow: 0 0 6px rgba(0, 246, 255, 0.2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.icon-btn {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: rgba(0, 246, 255, 0.1);
  color: var(--color-accent-primary);
}

.sign-out-icon:hover {
  background: rgba(255, 82, 82, 0.1);
  color: #ff8a80;
}

.desktop-mode-trigger:hover {
  background: rgba(0, 246, 255, 0.1);
  color: #00F6FF;
  box-shadow: 0 0 8px rgba(0, 246, 255, 0.2);
}

.icon-btn svg {
  display: block;
}

/* Settings Dropdown Menu */
.settings-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 12px;
  background: #1A1F35;
  border: 1px solid rgba(0, 246, 255, 0.3);
  border-radius: 12px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(0, 246, 255, 0.2);
  overflow: hidden;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.dropdown-header {
  padding: 12px 16px;
  background: linear-gradient(90deg, rgba(0, 246, 255, 0.15), rgba(0, 246, 255, 0.05));
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
}

.dropdown-header h3 {
  font-family: 'Orbitron', var(--font-display), sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: #00F6FF;
  letter-spacing: 1.5px;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: rgba(0, 246, 255, 0.08);
}

.dropdown-item .item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(0, 246, 255, 0.1);
  color: #00F6FF;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.dropdown-item:hover .item-icon {
  background: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.3);
}

.dropdown-item .item-text {
  flex: 1;
}

.dropdown-item .item-title {
  font-family: 'Rajdhani', var(--font-body), sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #E8EDFF;
  margin-bottom: 2px;
}

.dropdown-item .item-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

/* Transition animations */
.slide-fade-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.slide-fade-enter-from {
  transform: translateY(10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(10px);
  opacity: 0;
}

/* 1. Brand Header */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
}

.brand-ring {
  position: relative;
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00f3ff, #ff00ff);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    -2px -2px 8px rgba(0, 243, 255, 0.35),
    2px 2px 8px rgba(255, 0, 255, 0.35);
}

.brand-ring::before {
  content: '';
  position: absolute;
  top: 3px; left: 3px; right: 3px; bottom: 3px;
  background-color: #0a0f1a;
  border-radius: 50%;
  z-index: 1;
}

.brand-v {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.25rem;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 0 6px rgba(255, 255, 255, 0.7);
  position: relative;
  z-index: 2;
  margin-top: 1.5px;
}

.brand-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 17px;
  font-weight: 700;
  color: #00f3ff;
  margin: 0;
  letter-spacing: 1.5px;
  background: linear-gradient(90deg, #00f3ff, #00A3FF);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: none;
}

.serif-i {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: normal;
  -webkit-text-fill-color: transparent;
}

.brand-name {
  font-weight: 900;
  -webkit-text-fill-color: transparent;
}

.ai-glow {
  -webkit-text-fill-color: #00f3ff;
  animation: ai-breathe 4s ease-in-out infinite;
}

@keyframes ai-breathe {
  0%, 100% {
    -webkit-text-fill-color: rgba(0, 243, 255, 0.75);
    text-shadow: 0 0 4px rgba(0, 243, 255, 0.3);
  }
  50% {
    -webkit-text-fill-color: #00f3ff;
    text-shadow: 0 0 8px rgba(0, 243, 255, 0.8), 0 0 18px rgba(0, 243, 255, 0.5), 0 0 30px rgba(0, 243, 255, 0.25);
  }
}

/* 2. Actions Area */
.sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  width: 100%;
  padding: 12px 16px;
  border-radius: 8px; /* Slightly rounded corners like mockup */
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
  text-align: left;
}

/* Primary Button (New Chat) */
.action-btn.primary {
  background: linear-gradient(90deg, rgba(0, 246, 255, 0.1), rgba(0, 246, 255, 0.05));
  border: 1px solid rgba(0, 246, 255, 0.3);
  color: var(--color-accent-primary);
  position: relative;
  overflow: hidden;
}

.action-btn.primary::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: var(--color-accent-primary);
}

.action-btn.primary:hover {
  background: linear-gradient(90deg, rgba(0, 246, 255, 0.2), rgba(0, 246, 255, 0.1));
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.15);
  transform: translateX(2px);
}

/* Secondary Buttons (Search, History) */
.action-btn.secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.action-btn.secondary:hover {
  border-color: rgba(0, 246, 255, 0.3);
  color: white;
  background: rgba(255, 255, 255, 0.03);
}

.action-btn.secondary.active {
  background: rgba(0, 246, 255, 0.1);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

/* 3. History Section */
.history-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-label {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 12px;
  padding-left: 4px;
  letter-spacing: 1px;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px; /* Space for scrollbar */
}

/* Custom Scrollbar */
.conversations-list::-webkit-scrollbar {
  width: 4px;
}

.conversations-list::-webkit-scrollbar-track {
  background: transparent;
}

.conversations-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background: transparent;
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.conversation-item.active {
  background: linear-gradient(90deg, rgba(0, 246, 255, 0.1), transparent);
  border-left: 2px solid var(--color-accent-primary);
}

.item-icon {
  color: rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.conversation-item.active .item-icon {
  color: var(--color-accent-primary);
}

.item-content {
  flex: 1;
  overflow: hidden;
}

.item-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.conversation-item.active .item-title {
  color: white;
  font-weight: 600;
}

.item-meta {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

.delete-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  padding: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff5252;
  transform: scale(1.1);
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

/* 1. 给 AI 字母挂上呼吸动画 */
.text-highlight-ai {
  color: #ff00ff;
  font-weight: 800;
  animation: ai-highlight-breathe 4s infinite ease-in-out;
}

/* 2. 定义呼吸动画的关键帧 */
@keyframes ai-highlight-breathe {
  0%, 100% {
    text-shadow: 0 0 4px rgba(255, 0, 255, 0.4);
    opacity: 0.8;
  }
  50% {
    text-shadow: 0 0 10px rgba(255, 0, 255, 0.9), 0 0 20px rgba(255, 0, 255, 0.6);
    opacity: 1;
  }
}
</style>
