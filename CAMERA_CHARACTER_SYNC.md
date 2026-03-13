# 🎭 Camera-to-Character Emotion Sync Guide

## Overview

This guide shows you how to sync the **user's detected emotions** from the camera with the **3D character's expressions** in real-time.

---

## 🎯 Goal

When the camera detects your emotion (e.g., Happy), the 3D character should mirror that emotion immediately.

```
User Smiles → Camera Detects "Happy" → Character Shows Happy Expression
```

---

## 🔧 Implementation Steps

### Step 1: Create Emotion Store

First, create a new store to share emotion data between components.

**File**: `frontend/src/stores/emotionStore.js`

```javascript
import { defineStore } from 'pinia';

export const useEmotionStore = defineStore('emotion', {
  state: () => ({
    userEmotion: 'neutral',  // User's detected emotion
    characterEmotion: 'neutral',  // Character's current emotion
    syncEnabled: false  // Whether to sync emotions
  }),
  
  actions: {
    setUserEmotion(emotion) {
      this.userEmotion = emotion;
      
      // Auto-sync to character if enabled
      if (this.syncEnabled) {
        this.setCharacterEmotion(emotion);
      }
    },
    
    setCharacterEmotion(emotion) {
      this.characterEmotion = emotion;
    },
    
    toggleSync() {
      this.syncEnabled = !this.syncEnabled;
    }
  },
  
  getters: {
    isInSync: (state) => state.userEmotion === state.characterEmotion
  }
});
```

---

### Step 2: Update CameraView to Emit Emotions

Modify the `interpretExpression()` function in `CameraView.vue`:

```javascript
// Add at the top of script setup
import { useEmotionStore } from '../../stores/emotionStore';

const emotionStore = useEmotionStore();

// Modify interpretExpression function
const interpretExpression = (blendshapes) => {
  // ... existing detection logic ...
  
  // Update UI
  currentExpression.value = detectedEmotion;
  emotionEmoji.value = emotionMap[detectedEmotion] || '😐';
  
  // 🆕 SEND TO EMOTION STORE
  emotionStore.setUserEmotion(detectedEmotion.toLowerCase());
};
```

---

### Step 3: Update CharacterView to Listen for Emotions

Modify `CharacterView.vue` to watch the emotion store:

```javascript
// Add at the top of script setup
import { watch } from 'vue';
import { useEmotionStore } from '../../stores/emotionStore';

const emotionStore = useEmotionStore();

// Add this watch after onMounted
watch(
  () => emotionStore.characterEmotion,
  (newEmotion) => {
    console.log('🎭 Character emotion changed to:', newEmotion);
    
    // Map emotion names to VRM expression names
    const emotionMap = {
      'happy': 'happy',
      'sad': 'sad',
      'angry': 'angry',
      'surprised': 'surprised',
      'neutral': 'neutral',
      'blinking': 'neutral'  // VRM doesn't have blink expression
    };
    
    const vrmExpression = emotionMap[newEmotion] || 'neutral';
    setExpression(vrmExpression, 1.0);
  }
);
```

---

### Step 4: Add Sync Control UI

Add a toggle button to enable/disable emotion syncing.

**Option A: Add to CameraView.vue**

```vue
<!-- Add this button in the emotion-overlay section -->
<button 
  class="sync-toggle-btn" 
  @click="emotionStore.toggleSync()"
  :class="{ active: emotionStore.syncEnabled }"
>
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
  {{ emotionStore.syncEnabled ? 'Sync: ON' : 'Sync: OFF' }}
</button>
```

**CSS for sync button:**

```css
.sync-toggle-btn {
  background: rgba(123, 45, 255, 0.2);
  border: 1px solid rgba(123, 45, 255, 0.5);
  color: var(--color-accent-tertiary);
  padding: 8px 16px;
  font-family: var(--font-display);
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  clip-path: polygon(
    8px 0,
    100% 0,
    100% calc(100% - 8px),
    calc(100% - 8px) 100%,
    0 100%,
    0 8px
  );
}

.sync-toggle-btn.active {
  background: rgba(0, 246, 255, 0.3);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.4);
}

.sync-toggle-btn:hover {
  transform: translateX(3px);
  box-shadow: 0 0 20px rgba(123, 45, 255, 0.5);
}
```

---

## 🎨 Enhanced Features

### Feature 1: Emotion Smoothing

Prevent rapid emotion changes:

```javascript
// In CameraView.vue
const emotionHistory = ref([]);
const SMOOTHING_WINDOW = 5; // Last 5 detections

const interpretExpression = (blendshapes) => {
  // ... detection logic ...
  
  // Add to history
  emotionHistory.value.push(detectedEmotion);
  if (emotionHistory.value.length > SMOOTHING_WINDOW) {
    emotionHistory.value.shift();
  }
  
  // Find most common emotion
  const emotionCounts = {};
  emotionHistory.value.forEach(e => {
    emotionCounts[e] = (emotionCounts[e] || 0) + 1;
  });
  
  const smoothedEmotion = Object.keys(emotionCounts).reduce((a, b) => 
    emotionCounts[a] > emotionCounts[b] ? a : b
  );
  
  // Update with smoothed emotion
  currentExpression.value = smoothedEmotion;
  emotionEmoji.value = emotionMap[smoothedEmotion] || '😐';
  emotionStore.setUserEmotion(smoothedEmotion.toLowerCase());
};
```

---

### Feature 2: Emotion Transition Animation

Smooth transitions between emotions:

```javascript
// In CharacterView.vue
const transitionDuration = 500; // milliseconds
let currentWeight = 1.0;
let targetEmotion = 'neutral';

const transitionToEmotion = (emotion) => {
  const startTime = Date.now();
  const startWeight = currentWeight;
  
  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / transitionDuration, 1);
    
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    
    currentWeight = startWeight + (1 - startWeight) * eased;
    setExpression(emotion, currentWeight);
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };
  
  animate();
};

watch(
  () => emotionStore.characterEmotion,
  (newEmotion) => {
    const emotionMap = { /* ... */ };
    const vrmExpression = emotionMap[newEmotion] || 'neutral';
    transitionToEmotion(vrmExpression);
  }
);
```

---

### Feature 3: Emotion Intensity

Map blend shape intensity to expression strength:

```javascript
// In CameraView.vue
const interpretExpression = (blendshapes) => {
  // ... existing code ...
  
  // Calculate intensity (0.0 to 1.0)
  let intensity = 0;
  if (detectedEmotion === 'Happy') {
    intensity = (smileLeft + smileRight) / 2;
  } else if (detectedEmotion === 'Surprised') {
    intensity = jawOpen;
  }
  // ... etc
  
  // Send emotion with intensity
  emotionStore.setUserEmotion({
    type: detectedEmotion.toLowerCase(),
    intensity: intensity
  });
};
```

Then in CharacterView:

```javascript
watch(
  () => emotionStore.characterEmotion,
  (emotionData) => {
    const emotion = typeof emotionData === 'string' 
      ? emotionData 
      : emotionData.type;
    const intensity = typeof emotionData === 'object' 
      ? emotionData.intensity 
      : 1.0;
    
    const vrmExpression = emotionMap[emotion] || 'neutral';
    setExpression(vrmExpression, intensity);
  }
);
```

---

## 🎮 Advanced: Gesture Control

Detect hand gestures to control the character:

```javascript
// Example: Wave detection
const detectWaveGesture = (landmarks) => {
  // Hand landmarks from MediaPipe (requires hand tracking)
  const wristY = landmarks[0].y;
  const middleFingerY = landmarks[12].y;
  
  // If hand is raised and moving
  if (wristY < middleFingerY) {
    // Trigger wave animation on character
    characterViewRef.value.playAnimation('wave');
  }
};
```

---

## 📊 Debug Panel

Add a debug overlay to see sync status:

```vue
<!-- Add to TheMainLayout.vue -->
<div class="debug-panel" v-if="showDebug">
  <h3>🔍 Debug Info</h3>
  <div>User Emotion: {{ emotionStore.userEmotion }}</div>
  <div>Character Emotion: {{ emotionStore.characterEmotion }}</div>
  <div>Sync Enabled: {{ emotionStore.syncEnabled }}</div>
  <div>In Sync: {{ emotionStore.isInSync ? '✅' : '❌' }}</div>
</div>

<button @click="showDebug = !showDebug" class="debug-toggle">
  🐛 Debug
</button>
```

---

## 🧪 Testing Scenarios

Test these scenarios to ensure proper syncing:

1. **Happy Detection**
   - Smile at camera
   - Character should smile
   - Check transition smoothness

2. **Emotion Changes**
   - Change from happy to sad
   - Character should follow
   - Verify no lag

3. **Sync Toggle**
   - Disable sync
   - Change emotion
   - Character should NOT change
   - Re-enable sync
   - Character should update

4. **Edge Cases**
   - No face detected → Character stays neutral
   - Multiple rapid changes → Smoothing works
   - Camera stopped → Character keeps last emotion

---

## 🎯 Performance Tips

1. **Throttle Updates**: Don't update character every frame
   ```javascript
   let lastUpdate = 0;
   const UPDATE_INTERVAL = 100; // ms
   
   if (Date.now() - lastUpdate > UPDATE_INTERVAL) {
     emotionStore.setUserEmotion(emotion);
     lastUpdate = Date.now();
   }
   ```

2. **Debounce Emotion Changes**: Wait for stable emotion
   ```javascript
   let emotionTimeout;
   const DEBOUNCE_DELAY = 300;
   
   const debouncedSetEmotion = (emotion) => {
     clearTimeout(emotionTimeout);
     emotionTimeout = setTimeout(() => {
       emotionStore.setUserEmotion(emotion);
     }, DEBOUNCE_DELAY);
   };
   ```

---

## 📝 Complete File Structure

After implementation:

```
frontend/src/
├── stores/
│   ├── chatStore.js
│   ├── uiStore.js
│   └── emotionStore.js          ← NEW
│
├── components/
│   ├── camera/
│   │   └── CameraView.vue       ← MODIFIED (emit emotions)
│   ├── character/
│   │   └── CharacterView.vue    ← MODIFIED (listen emotions)
│   └── layout/
│       └── TheMainLayout.vue    ← MODIFIED (add sync UI)
```

---

## 🚀 Quick Start

1. **Create emotion store**:
   ```bash
   # Create new file
   touch frontend/src/stores/emotionStore.js
   ```

2. **Copy emotion store code** from Step 1 above

3. **Update CameraView.vue** with emotion emission (Step 2)

4. **Update CharacterView.vue** with emotion listening (Step 3)

5. **Add sync toggle UI** (Step 4)

6. **Test in browser**:
   - Start backend and frontend
   - Enable camera
   - Toggle sync ON
   - Smile → Character smiles! 😊

---

## 🎉 Result

You now have a **fully interactive AI character** that:
- ✅ Detects your emotions via camera
- ✅ Mirrors your expressions in real-time
- ✅ Allows you to toggle sync on/off
- ✅ Smoothly transitions between emotions
- ✅ Handles edge cases gracefully

---

**Next Steps**: Consider adding:
- Voice emotion detection (from microphone)
- Gesture-based controls
- Emotion history timeline
- Multi-user emotion tracking

---

**Last Updated**: October 8, 2025  
**Version**: 1.0.0
