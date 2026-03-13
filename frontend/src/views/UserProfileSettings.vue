<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- Content -->
      <div class="settings-content">
        <!-- Header -->
        <div class="content-header">
          <h1 class="page-title">USER PROFILE</h1>
          <p class="page-subtitle">Manage your account information</p>
        </div>

        <div class="settings-section">
          <h2 class="section-title">Personal Information</h2>
          
          <div class="form-group">
            <label>Profile Picture</label>
            <div class="avatar-upload">
              <img :src="userAvatar" alt="Avatar" class="preview-avatar" />
              <button class="upload-btn">Change Avatar</button>
            </div>
          </div>

          <div class="form-group">
            <label>Display Name</label>
            <input type="text" v-model="displayName" class="input-field" placeholder="Enter your name" />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="email" class="input-field" placeholder="your.email@example.com" disabled />
            <span class="field-hint">Email cannot be changed</span>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">Account Settings</h2>
          
          <div class="form-group">
            <label>Language</label>
            <select v-model="language" class="input-field">
              <option value="en">English</option>
              <option value="zh">中文</option>
              <option value="ja">日本語</option>
            </select>
          </div>

          <div class="form-group">
            <label>Theme</label>
            <select v-model="theme" class="input-field">
              <option value="dark">Dark (Cyberpunk)</option>
              <option value="light">Light</option>
            </select>
          </div>
        </div>

        <div class="actions">
          <button class="btn-save" @click="saveSettings">Save Changes</button>
          <button class="btn-cancel" @click="goBack">Back to Chat</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const displayName = ref('Sean');
const email = ref('sean@example.com');
const userAvatar = ref('https://api.dicebear.com/7.x/avataaars/svg?seed=Sean');
const language = ref('en');
const theme = ref('dark');

onMounted(() => {
  // Load user data from localStorage
  const userData = localStorage.getItem('user');
  if (userData) {
    const user = JSON.parse(userData);
    displayName.value = user.name || 'Sean';
    email.value = user.email || 'sean@example.com';
    userAvatar.value = user.picture || 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sean';
  }
});

const goBack = () => {
  router.push('/chat');
};

const saveSettings = () => {
  console.log('💾 Saving user profile settings...');
  // TODO: Save to backend
  alert('Settings saved successfully!');
};
</script>

<style scoped>
.settings-page {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: #0E101B;
  color: #E8EDFF;
  font-family: 'Rajdhani', sans-serif;
  padding: 20px;
  overflow-y: auto;
  z-index: 100;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.settings-content {
  background: rgba(26, 31, 53, 0.5);
  border: 1px solid rgba(0, 246, 255, 0.2);
  border-radius: 12px;
  padding: 32px;
  backdrop-filter: blur(10px);
}

.content-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
}

.page-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  color: #00F6FF;
  margin-bottom: 12px;
  letter-spacing: 2px;
  text-shadow: 0 0 20px rgba(0, 246, 255, 0.5);
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  margin: 0;
}

.settings-content {
  background: rgba(26, 31, 53, 0.5);
  border: 1px solid rgba(0, 246, 255, 0.2);
  border-radius: 12px;
  padding: 32px;
  backdrop-filter: blur(10px);
}

.settings-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.settings-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-family: 'Rajdhani', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #00F6FF;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 246, 255, 0.3);
  border-radius: 8px;
  color: #E8EDFF;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  transition: all 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: #00F6FF;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.2);
}

.input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.field-hint {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #00F6FF;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.4);
}

.upload-btn {
  background: rgba(0, 246, 255, 0.1);
  border: 1px solid rgba(0, 246, 255, 0.3);
  color: #00F6FF;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.upload-btn:hover {
  background: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.3);
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
}

.btn-save {
  background: linear-gradient(90deg, #00F6FF, #00A3FF);
  border: none;
  color: #0E101B;
  padding: 12px 32px;
  border-radius: 8px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-size: 16px;
  font-weight: 700;
  transition: all 0.2s;
}

.btn-save:hover {
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.5);
  transform: translateY(-2px);
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.8);
  padding: 12px 32px;
  border-radius: 8px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-cancel svg {
  width: 18px;
  height: 18px;
}
</style>
