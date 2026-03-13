<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- Content -->
      <div class="settings-content">
        <!-- Header -->
        <div class="content-header">
          <h1 class="page-title">VOICE SETTINGS</h1>
          <p class="page-subtitle">Upload and customize your character's voice</p>
        </div>

        <div class="settings-section">
          <h2 class="section-title">🎭 Character Voice Selection</h2>
          
          <div class="form-group">
            <label>Current Active Character</label>
            <div class="character-selector">
              <div v-if="isLoadingCharacters" class="loading-indicator">
                Loading characters...
              </div>
              <div v-else-if="availableCharacters.length === 0" class="no-characters">
                No characters available. Please check server connection.
                <br><small>Backend should be running on http://localhost:8000</small>
              </div>
              <div v-else>
                <div 
                  v-for="character in availableCharacters" 
                  :key="character.id"
                  class="character-option"
                  :class="{ active: character.is_active }"
                  @click="setActiveCharacter(character.id)"
                >
                  <div class="character-info">
                    <div class="character-name">{{ character.name }}</div>
                    <div class="character-type">{{ character.is_custom ? 'Custom' : 'Default' }}</div>
                  </div>
                  
                  <div class="character-actions">
                    <div v-if="character.is_active" class="active-indicator">✓</div>
                    
                    <!-- Delete Button for Custom Characters -->
                    <button 
                      v-if="character.is_custom" 
                      class="delete-btn"
                      @click.stop="deleteCharacter(character.id, character.name)"
                      title="Delete Voice"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <button class="refresh-btn" @click="loadCharacters" :disabled="isLoadingCharacters">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 2v6h6m2 0a9 9 0 11-9 9m11-4v6h-6m-2 0a9 9 0 109-9"/>
              </svg>
              Refresh Characters
            </button>
            <!-- Debug info -->
            <div v-if="availableCharacters.length > 0" class="debug-info">
              <small>Loaded {{ availableCharacters.length }} character(s)</small>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">🎤 Upload Voice</h2>
          
          <div class="form-group">
            <label>Voice File</label>
            <div class="upload-area">
              <input type="file" accept=".wav,.mp3,.ogg" @change="handleVoiceUpload" id="voiceUpload" hidden />
              <label for="voiceUpload" class="upload-label">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <span>{{ uploadedFileName || 'Click to upload voice file (WAV, MP3, OGG)' }}</span>
              </label>
            </div>
          </div>

          <div class="form-group" v-if="uploadedFileName">
            <div class="file-info">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
              <span>{{ uploadedFileName }}</span>
              <svg v-if="uploadSuccess" class="success-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h2 class="section-title">🔊 Test Voice</h2>
          
          <div class="form-group">
            <label>Enter Text to Test</label>
            <textarea 
              v-model="testText" 
              class="text-area" 
              placeholder="Type something to hear how your voice sounds..."
              rows="4"
            ></textarea>
          </div>

          <div class="button-group">
            <button 
              class="test-btn" 
              @click="testVoice" 
              :disabled="!uploadedFileName || isTesting || isUploading"
            >
              <svg v-if="!isTesting" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <svg v-else class="spinner" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
              </svg>
              {{ isTesting ? 'Generating...' : 'Test Voice' }}
            </button>

            <button 
              class="apply-btn" 
              @click="applyVoice" 
              :disabled="!uploadedFileName || isApplying || isUploading"
            >
              <svg v-if="!isApplying" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <svg v-else class="spinner" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
              </svg>
              {{ isApplying ? 'Applying...' : 'Apply Voice to 3D Model' }}
            </button>
          </div>
        </div>

        <div class="actions">
          <button class="btn-cancel" @click="goBack">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Back to Chat
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const uploadedFileName = ref('');
const uploadedFile = ref(null);
const characterId = ref('');
const testText = ref('Hello! This is a test of my custom voice.');
const isUploading = ref(false);
const isTesting = ref(false);
const isApplying = ref(false);
const currentAudio = ref(null);
const uploadSuccess = ref(false);
const availableCharacters = ref([]);
const isLoadingCharacters = ref(false);

// Load characters when component mounts
const loadCharacters = async () => {
  isLoadingCharacters.value = true;
  try {
    console.log('🔄 Loading characters from API...');
    const response = await fetch('http://localhost:8000/api/voice/characters');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('📦 API Response:', result);
    
    if (result.status === 'success') {
      availableCharacters.value = result.characters || [];
      console.log('✅ Characters loaded successfully:', result.characters);
      console.log('📊 Character count:', availableCharacters.value.length);
    } else {
      console.error('❌ API returned error:', result);
      throw new Error(result.message || 'Failed to load characters');
    }
  } catch (error) {
    console.error('❌ Error loading characters:', error);
    console.log('💡 Make sure backend is running on http://localhost:8000');
    availableCharacters.value = [];
  } finally {
    isLoadingCharacters.value = false;
  }
};

// Set active character
const setActiveCharacter = async (characterId) => {
  try {
    console.log('🎭 Setting active character:', characterId);
    
    const formData = new FormData();
    formData.append('character_id', characterId);

    const response = await fetch('http://localhost:8000/api/voice/set-active-character', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    if (result.status === 'success') {
      // Update local state
      availableCharacters.value.forEach(char => {
        char.is_active = (char.id === characterId);
      });
      console.log('✅ Character activated:', result.character_name);
      alert(`Active character set to ${result.character_name}!`);
    } else {
      throw new Error(result.message || 'Failed to set active character');
    }
  } catch (error) {
    console.error('❌ Error setting character:', error);
    alert(`Failed to set active character: ${error.message}`);
  }
};

const deleteCharacter = async (id, name) => {
  if (!confirm(`Are you sure you want to delete voice "${name}"?\n\nThis cannot be undone.`)) {
    return;
  }

  try {
    const response = await fetch(`http://localhost:8000/api/voice/character/${id}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
       const result = await response.json();
       throw new Error(result.message || 'Failed to delete character');
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('🗑️ Character deleted:', id);
      // Remove from local list immediately
      availableCharacters.value = availableCharacters.value.filter(c => c.id !== id);
      
      // If we deleted the active character, reload to reflect default
      loadCharacters();
    } else {
      throw new Error(result.message || 'Failed to delete character');
    }
  } catch (error) {
    console.error('❌ Delete error:', error);
    alert(`Failed to delete character: ${error.message}`);
  }
};

const goBack = () => {
  router.push('/chat');
};

const handleVoiceUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    alert('File is too large! Maximum size is 10MB.');
    return;
  }

  uploadedFileName.value = file.name;
  uploadedFile.value = file;
  isUploading.value = true;  // Add this line
  uploadSuccess.value = false;

  try {
    console.log('🎵 Uploading voice file:', file.name);
    
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/api/voice/upload', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    if (result.status === 'success') {
      characterId.value = result.character_id;
      uploadSuccess.value = true;
      console.log('✅ Voice uploaded successfully:', result.character_id);
    } else {
      throw new Error(result.message || 'Upload failed');
    }
  } catch (error) {
    console.error('❌ Upload error:', error);
    alert(`Failed to upload voice file: ${error.message}`);
    uploadedFileName.value = '';
    uploadedFile.value = null;
    characterId.value = '';
    uploadSuccess.value = false;
  } finally {
    isUploading.value = false;
  }
};

const testVoice = async () => {
  console.log('🔍 Testing voice - Character ID:', characterId.value);
  console.log('🔍 Uploaded filename:', uploadedFileName.value);
  
  if (!characterId.value) {
    console.error('❌ No character ID found');
    alert('Please upload a voice file first!');
    return;
  }
  if (!testText.value.trim()) {
    alert('Please enter some text to test!');
    return;
  }

  isTesting.value = true;

  try {
    console.log('🔊 Testing voice with text:', testText.value);

    const formData = new FormData();
    formData.append('character_id', characterId.value);
    formData.append('text', testText.value);

    const response = await fetch('http://localhost:8000/api/voice/test-custom', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    if (result.status === 'success' && result.audio_url) {
      console.log('✅ Test audio generated:', result.audio_url);
      
      // Stop any currently playing audio
      if (currentAudio.value) {
        currentAudio.value.pause();
        currentAudio.value = null;
      }

      // Play the test audio
      const audioUrl = `http://localhost:8000${result.audio_url}`;
      const audio = new Audio(audioUrl);
      currentAudio.value = audio;

      audio.addEventListener('ended', () => {
        console.log('✅ Test audio finished playing');
        currentAudio.value = null;
      });

      audio.addEventListener('error', (e) => {
        console.error('❌ Error playing audio:', e);
        alert('Failed to play audio. Please check the console for details.');
        currentAudio.value = null;
      });

      await audio.play();
      console.log('🔊 Playing test audio...');
      
    } else {
      throw new Error(result.message || 'Voice generation failed');
    }
  } catch (error) {
    console.error('❌ Test error:', error);
    alert(`Failed to test voice: ${error.message}`);
  } finally {
    isTesting.value = false;
  }
};

const applyVoice = async () => {
  if (!characterId.value) {
    alert('Please upload a voice file first!');
    return;
  }

  // Prompt user for custom voice name
  const voiceName = prompt(
    `Give your custom voice a name:\n\n` +
    `This will be saved permanently and used for all future conversations.\n\n` +
    `Original file: ${uploadedFileName.value}`,
    `My Custom Voice`
  );

  if (!voiceName || !voiceName.trim()) {
    return; // User cancelled or entered empty name
  }

  const finalVoiceName = voiceName.trim();

  const confirmed = confirm(
    `Apply voice "${finalVoiceName}"?\n\n` +
    `This will replace the current character voice.\n\n` +
    `Source: ${uploadedFileName.value}`
  );

  if (!confirmed) return;

  isApplying.value = true;

  try {
    console.log('✅ Applying voice to 3D model:', characterId.value, 'as', finalVoiceName);

    const formData = new FormData();
    formData.append('character_id', characterId.value);
    formData.append('voice_name', finalVoiceName);

    const response = await fetch('http://localhost:8000/api/voice/apply-custom', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    if (result.status === 'success') {
      console.log('✅ Voice applied successfully');
      alert(
        `✅ Success!\n\n` +
        `Voice "${finalVoiceName}" has been applied.\n\n` +
        `Your character will now use this voice in all conversations!`
      );
      
      // Clear the form since voice is now permanent
      uploadedFileName.value = '';
      uploadedFile.value = null;
      characterId.value = '';
      uploadSuccess.value = false;
      
      // Optionally navigate back to chat
      setTimeout(() => {
        router.push('/chat');
      }, 1000);
    } else {
      throw new Error(result.message || 'Failed to apply voice');
    }
  } catch (error) {
    console.error('❌ Apply error:', error);
    alert(`Failed to apply voice: ${error.message}`);
  } finally {
    isApplying.value = false;
  }
};

// Initialize component - Load characters when component mounts
onMounted(() => {
  loadCharacters();
});
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

.text-area {
  width: 100%;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 246, 255, 0.3);
  border-radius: 8px;
  color: #E8EDFF;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  transition: all 0.2s;
  resize: vertical;
  min-height: 100px;
}

.text-area:focus {
  outline: none;
  border-color: #00F6FF;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.2);
}

.text-area::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-start;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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

.upload-area {
  border: 2px dashed rgba(0, 246, 255, 0.3);
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  background: rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #00F6FF;
  background: rgba(0, 246, 255, 0.05);
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.upload-label svg {
  color: #00F6FF;
}

.upload-label span {
  font-size: 14px;
  font-weight: 600;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(0, 246, 255, 0.1);
  border: 1px solid rgba(0, 246, 255, 0.3);
  border-radius: 8px;
  color: #00F6FF;
  font-size: 14px;
  font-weight: 600;
}

.file-info svg {
  flex-shrink: 0;
}

.file-info .success-icon {
  margin-left: auto;
  color: #00FF88;
  filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.6));
  animation: checkmark-appear 0.3s ease-out;
}

@keyframes checkmark-appear {
  0% {
    opacity: 0;
    transform: scale(0.5);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}
.character-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid rgba(0, 246, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
}

.character-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.character-option:hover {
  background: rgba(0, 246, 255, 0.05);
  border-color: rgba(0, 246, 255, 0.3);
}

.character-option.active {
  background: rgba(0, 246, 255, 0.1);
  border-color: #00F6FF;
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.2);
}

.character-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.character-name {
  font-size: 16px;
  font-weight: 600;
  color: #E8EDFF;
}

.character-type {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

.active-indicator {
  color: #00FF88;
  font-size: 18px;
  font-weight: bold;
  filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.6));
}

.character-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.delete-btn {
  background: transparent;
  border: none;
  color: rgba(255, 50, 50, 0.7);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: rgba(255, 50, 50, 0.1);
  color: #FF3333;
  transform: scale(1.1);
}



.loading-indicator {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  transition: all 0.2s;
  align-self: flex-start;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-characters {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  margin-bottom: 12px;
}

.debug-info {
  text-align: center;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.5);
}

.test-btn {
  background: rgba(0, 246, 255, 0.1);
  border: 1px solid rgba(0, 246, 255, 0.3);
  color: #00F6FF;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.test-btn:hover:not(:disabled) {
  background: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.3);
}

.test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.apply-btn {
  background: linear-gradient(90deg, #00F6FF, #00A3FF);
  border: none;
  color: #0E101B;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.apply-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.5);
  transform: translateY(-2px);
}

.apply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
