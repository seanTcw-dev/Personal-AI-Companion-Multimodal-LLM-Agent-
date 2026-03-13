<template>
  <div class="email-client">
    <!-- Sidebar -->
    <div class="email-sidebar">
      <div class="sidebar-header">
        <h2>MailBox</h2>
        <button class="compose-btn" @click="generateNewEmail">+ New Mock Email</button>
      </div>
      
      <nav class="email-nav">
        <a href="#" :class="{ active: currentTab === 'inbox' }" @click.prevent="currentTab = 'inbox'">
          <span class="icon">📥</span> Inbox
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
        </a>
        <a href="#" :class="{ active: currentTab === 'news' }" @click.prevent="currentTab = 'news'">
          <span class="icon">📰</span> News Feed
        </a>
        <a href="#" :class="{ active: currentTab === 'sent' }" @click.prevent="currentTab = 'sent'">
          <span class="icon">📤</span> Sent
        </a>
        <a href="#" :class="{ active: currentTab === 'trash' }" @click.prevent="currentTab = 'trash'">
          <span class="icon">🗑️</span> Trash
        </a>
      </nav>

      <div class="back-link">
        <router-link to="/chat" class="nav-item">
          ⬅ Back to Main Interface
        </router-link>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="email-content">
      
      <!-- INBOX VIEW -->
      <div v-if="currentTab === 'inbox'" class="inbox-view">
        <div class="content-header">
          <h3>Inbox</h3>
          <button @click="handleRefresh" class="refresh-btn">🔄 Refresh</button>
        </div>
        
        <div class="email-list">
          <div 
            v-for="email in emails" 
            :key="email.id" 
            class="email-item" 
            :class="{ unread: !email.read, selected: selectedEmail?.id === email.id }"
            @click="selectEmail(email)"
          >
            <div class="email-avatar">{{ email.sender_name[0] }}</div>
            <div class="email-info">
              <div class="email-top">
                <span class="sender">{{ email.sender_name }}</span>
                <span class="time">{{ formatTime(email.timestamp) }}</span>
              </div>
              <div class="subject">{{ email.subject }}</div>
              <div class="snippet">{{ email.body.substring(0, 50) }}...</div>
            </div>
          </div>
        </div>
      </div>

      <!-- NEWS VIEW -->
      <div v-if="currentTab === 'news'" class="news-view">
        <div class="content-header">
          <h3>Daily News Briefing</h3>
          <button @click="handleRefresh" class="refresh-btn">🔄 Refresh</button>
        </div>
        
        <div class="news-grid">
          <div v-for="item in news" :key="item.id" class="news-card">
            <div class="news-source">{{ item.source }}</div>
            <div class="news-title">{{ item.title }}</div>
            <div class="news-summary">{{ item.summary }}</div>
            <div class="news-time">{{ formatTime(item.timestamp) }}</div>
          </div>
        </div>
      </div>

      <!-- EMAIL READING PANE (Overlay or Split) -->
      <div v-if="selectedEmail && currentTab === 'inbox'" class="email-reading-pane">
        <div class="reading-header">
          <button @click="selectedEmail = null" class="close-btn">✖</button>
          <h2>{{ selectedEmail.subject }}</h2>
          <div class="meta">
            <span class="from">From: {{ selectedEmail.sender_name }} &lt;{{ selectedEmail.sender_email }}&gt;</span>
            <span class="date">{{ formatTime(selectedEmail.timestamp) }}</span>
          </div>
        </div>
        <div class="reading-body">
          {{ selectedEmail.body }}
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { fetchEmails, refreshEmails, fetchNews, refreshNews, generateEmail } from '../services/emailService';

const emails = ref([]);
const news = ref([]);
const unreadCount = ref(0);
const currentTab = ref('inbox');
const selectedEmail = ref(null);

const loadData = async () => {
  // Just fetch existing data
  const emailData = await fetchEmails();
  emails.value = emailData.emails;
  unreadCount.value = emailData.unread_count;

  const newsData = await fetchNews();
  news.value = newsData.news;
};

const handleRefresh = async () => {
  // Trigger generation of new data
  if (currentTab.value === 'inbox') {
    await refreshEmails();
  } else if (currentTab.value === 'news') {
    await refreshNews();
  }
  // Then load everything
  await loadData();
};

const generateNewEmail = async () => {
  await generateEmail();
  await loadData();
};

const selectEmail = (email) => {
  selectedEmail.value = email;
  // TODO: Mark as read via API
  if (!email.read) {
    email.read = true;
    unreadCount.value = Math.max(0, unreadCount.value - 1);
  }
};

const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
/* Cyberpunk / Modern Email Client Styles */
.email-client {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: #0E101B;
  color: #E8EDFF;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

/* Sidebar */
.email-sidebar {
  width: 250px;
  background-color: rgba(26, 31, 53, 0.9);
  border-right: 1px solid rgba(0, 246, 255, 0.2);
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.sidebar-header h2 {
  font-family: 'Orbitron', sans-serif;
  color: #00F6FF;
  margin-bottom: 1rem;
}

.compose-btn {
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(45deg, #00F6FF, #00B7FF);
  border: none;
  border-radius: 4px;
  color: #000;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.4);
  transition: transform 0.2s;
}

.compose-btn:hover {
  transform: scale(1.02);
}

.email-nav {
  margin-top: 2rem;
  flex: 1;
}

.email-nav a {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  color: #9FADC6;
  text-decoration: none;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  transition: background 0.2s;
}

.email-nav a:hover, .email-nav a.active {
  background-color: rgba(0, 246, 255, 0.1);
  color: #00F6FF;
}

.email-nav .icon {
  margin-right: 10px;
}

.badge {
  margin-left: auto;
  background-color: #FF00E0;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8rem;
}

/* Main Content */
.email-content {
  flex: 1;
  display: flex;
  position: relative;
  background-image: 
    linear-gradient(rgba(14, 16, 27, 0.95), rgba(14, 16, 27, 0.95)),
    url('https://www.transparenttextures.com/patterns/cubes.png');
}

.inbox-view, .news-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow: hidden;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
  padding-bottom: 0.5rem;
}

.refresh-btn {
  background: transparent;
  border: 1px solid #7B2DFF;
  color: #7B2DFF;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background: rgba(123, 45, 255, 0.1);
}

/* Email List */
.email-list {
  overflow-y: auto;
  flex: 1;
}

.email-item {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background 0.2s;
}

.email-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.email-item.selected {
  background-color: rgba(0, 246, 255, 0.1);
  border-left: 3px solid #00F6FF;
}

.email-avatar {
  width: 40px;
  height: 40px;
  background-color: #7B2DFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 1rem;
}

.email-info {
  flex: 1;
}

.email-top {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.sender {
  font-weight: bold;
  color: #E8EDFF;
}

.time {
  color: #9FADC6;
  font-size: 0.8rem;
}

.subject {
  font-weight: 500;
  color: #E8EDFF;
  margin-bottom: 2px;
}

.snippet {
  color: #9FADC6;
  font-size: 0.85rem;
}

.email-item.unread .subject,
.email-item.unread .sender {
  color: #00F6FF;
  font-weight: 800;
}

/* Reading Pane */
.email-reading-pane {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background-color: #1A1F35;
  border-left: 1px solid rgba(0, 246, 255, 0.3);
  padding: 2rem;
  box-shadow: -5px 0 15px rgba(0,0,0,0.5);
  animation: slideIn 0.3s ease;
  z-index: 10;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.reading-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  background: none;
  border: none;
  color: #9FADC6;
  font-size: 1.5rem;
  cursor: pointer;
}

.meta {
  margin-top: 0.5rem;
  color: #9FADC6;
  font-size: 0.9rem;
  display: flex;
  justify-content: space-between;
}

.reading-body {
  line-height: 1.6;
  color: #E8EDFF;
  white-space: pre-wrap;
}

/* News Grid */
.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  overflow-y: auto;
}

.news-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(123, 45, 255, 0.3);
  padding: 1rem;
  border-radius: 8px;
}

.news-source {
  color: #FF00E0;
  font-size: 0.8rem;
  text-transform: uppercase;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.news-title {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #E8EDFF;
}

.news-summary {
  color: #9FADC6;
  font-size: 0.9rem;
  line-height: 1.4;
}

.back-link {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.back-link .nav-item {
  color: #9FADC6;
  text-decoration: none;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.back-link .nav-item:hover {
  color: #00F6FF;
}
</style>
