<template>
  <div class="camera-view">
    <div class="camera-placeholder" v-show="!cameraActive">
      <div class="camera-text">Camera Feed</div>
      <div class="camera-icon pulse-animation">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
          <path d="M0 5a2 2 0 0 1 2-2h7.5a2 2 0 0 1 1.983 1.738l3.11-1.382A1 1 0 0 1 16 4.269v7.462a1 1 0 0 1-1.406.913l-3.111-1.382A2 2 0 0 1 9.5 13H2a2 2 0 0 1-2-2V5z"/>
        </svg>
      </div>
      <div class="camera-status">{{ loadingStatus || 'No active camera' }}</div>
      <button class="camera-button" @click="toggleCamera" :disabled="isLoading">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
          <circle cx="12" cy="13" r="4"></circle>
        </svg>
        {{ isLoading ? 'Loading...' : 'Enable Camera' }}
      </button>
    </div>
    
    <!-- Video feed -->
    <video ref="videoElement" class="camera-feed" :class="{ active: cameraActive }" autoplay playsinline muted></video>
    
    <!-- Floating toast notification (independent of gesture detection state) -->
    <transition name="toast">
      <div class="gesture-toast" v-if="toastVisible">
        <span class="toast-icon">{{ toastIcon }}</span>
        <span class="toast-message">{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- Emotion detection UI (shown when camera is active) -->
    <div class="emotion-overlay" v-show="cameraActive">
      <div class="emotion-badge">
        <span class="emotion-icon">{{ emotionEmoji }}</span>
        <span class="emotion-text">{{ currentExpression }}</span>
        <span class="emotion-source" v-if="emotionSource">{{ emotionSource }}</span>
      </div>
      
      <!-- Gesture tracking UI -->
      <div class="gesture-badge" v-if="currentGesture !== 'None'">
        <span class="emotion-icon">{{ gestureIcon }}</span>
        <div class="gesture-info">
          <span class="emotion-text">{{ currentGesture }}</span>
          <span class="gesture-action" v-if="gestureAction">{{ gestureAction }}</span>
        </div>
      </div>
      
      <!-- Face detection indicator -->
      <div class="detection-status" :class="{ 'face-detected': faceDetected }">
        <div class="status-dot"></div>
        {{ faceDetected ? 'Face Detected' : 'No Face' }}
      </div>
      
      <!-- Audio emotion detector -->
      <AudioEmotionDetector 
        @emotionDetected="handleAudioEmotion" 
        @volumeLevel="handleVolumeLevel"
      />
      
      <!-- Stop camera button -->
      <button class="stop-camera-btn" @click="stopCamera">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        </svg>
        Stop Camera
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { FaceLandmarker, GestureRecognizer, FilesetResolver } from '@mediapipe/tasks-vision';
import html2canvas from 'html2canvas';
import { websocketService } from '../../services/websocket';
import { useChatStore } from '../../stores/chatStore';
import AudioEmotionDetector from './AudioEmotionDetector.vue';

// --- Variables ---
const videoElement = ref(null);
const currentExpression = ref('Neutral');
const emotionEmoji = ref('😐');
const emotionSource = ref(''); // '📹' for camera, '🎤' for audio
const cameraActive = ref(false);
const faceDetected = ref(false);
const isLoading = ref(false);
const loadingStatus = ref('');

// Gesture variables
const currentGesture = ref('None');
const gestureAction = ref('');
const gestureIcon = ref('✋');
let lastGestureTime = 0;
const GESTURE_COOLDOWN = 2000; // 2 seconds between actions

// Toast notification state
const toastVisible = ref(false);
const toastMessage = ref('');
const toastIcon = ref('✅');
let toastTimer = null;

// Shutter flash: dispatch a global event for the layout to handle (sound + flash are in TheMainLayout)
const triggerShutterEffect = () => {
  window.dispatchEvent(new CustomEvent('camera:shutter'));
};

const showToast = (icon, message, duration = 3000) => {
  if (toastTimer) clearTimeout(toastTimer);
  toastIcon.value = icon;
  toastMessage.value = message;
  toastVisible.value = true;
  toastTimer = setTimeout(() => {
    toastVisible.value = false;
  }, duration);
};

// Emotion tracking for auto-messages
let lastEmotionSent = '';
let emotionStartTime = 0;
const EMOTION_DURATION_THRESHOLD = 3000; // 3 seconds
const emotionHistory = [];
const EMOTION_HISTORY_SIZE = 10;

const chatStore = useChatStore();

let faceLandmarker = null;
let gestureRecognizer = null;
let animationFrameId = null;

// Emotion mapping
const emotionMap = {
  'Happy': '😊',
  'Sad': '😢',
  'Surprised': '😲',
  'Angry': '😠',
  'Neutral': '😐',
  'Blinking': '😌'
};

// --- Core Functions ---

// 1. Initialize MediaPipe Face Landmarker & Gesture Recognizer
const initAIModels = async () => {
  try {
    loadingStatus.value = 'Loading face model...';
    console.log('🔄 Initializing MediaPipe Face Landmarker...');
    
    const filesetResolver = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
    );
    
    // --- REQUIRED: Face Landmarker (blocks camera start if it fails) ---
    faceLandmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
      baseOptions: {
        modelAssetPath: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task`,
        delegate: "GPU",
      },
      outputFaceBlendshapes: true,
      runningMode: 'VIDEO',
      numFaces: 1
    });
    console.log('✅ Face Landmarker loaded!');

    // --- OPTIONAL: Gesture Recognizer (camera still works if this fails) ---
    loadingStatus.value = 'Loading gesture model...';
    try {
      gestureRecognizer = await GestureRecognizer.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath: `https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task`,
          delegate: "GPU",
        },
        runningMode: 'VIDEO',
        numHands: 2
      });
      console.log('✅ Gesture Recognizer loaded!');
    } catch (gestureError) {
      // Non-fatal: camera works without gesture recognition
      console.warn('⚠️ Gesture Recognizer failed to load (gestures disabled):', gestureError);
      gestureRecognizer = null;
    }
    
    loadingStatus.value = '';
    return true;
  } catch (error) {
    console.error('❌ Error loading Face Landmarker:', error);
    loadingStatus.value = 'Failed to load face model';
    alert('Failed to load face detection model. Please check your internet connection.');
    return false;
  }
};

// 2. Enable camera
const enableCam = async () => {
  if (!faceLandmarker) {
    console.log("⚠️ Face Landmarker not loaded yet.");
    return false;
  }
  
  try {
    loadingStatus.value = 'Requesting camera access...';
    // --- Optimized code with precise camera control ---
    const constraints = {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 }
      }
    };
    
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (constraintError) {
      console.warn("⚠️ Failed with ideal constraints, retrying with basic config...", constraintError);
      // Fallback to basic constraints
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
    }
    
    videoElement.value.srcObject = stream;
    
    // Wait for video to be ready
    await new Promise((resolve) => {
      videoElement.value.addEventListener("loadeddata", resolve, { once: true });
    });
    
    cameraActive.value = true;
    loadingStatus.value = '';
    
    // Start detection loop
    predictWebcam();
    
    console.log('✅ Camera enabled and detection started');
    return true;
  } catch (err) {
    console.error("❌ Error accessing webcam:", err);
    loadingStatus.value = '';
    
    let errorMsg = 'Could not access the camera.';
    
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      errorMsg = 'Camera permission denied. Please allow camera access in your browser settings.';
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      errorMsg = 'No camera found. Please connect a camera.';
    } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
      errorMsg = 'Camera is in use by another application. Please close other apps using the camera.';
    } else {
      errorMsg = `Camera error: ${err.message || err.name}`;
    }
    
    alert(errorMsg);
    return false;
  }
};

// 3. Detection loop
const predictWebcam = () => {
  if (!videoElement.value || videoElement.value.readyState < 2) {
    animationFrameId = requestAnimationFrame(predictWebcam);
    return;
  }

  const startTimeMs = performance.now();
  
  try {
    // Face Detection
    const faceResults = faceLandmarker.detectForVideo(videoElement.value, startTimeMs);

    if (faceResults.faceBlendshapes && faceResults.faceBlendshapes.length > 0) {
      faceDetected.value = true;
      // Interpret expression from blend shapes
      interpretExpression(faceResults.faceBlendshapes[0].categories);
    } else {
      faceDetected.value = false;
      currentExpression.value = 'No Face';
      emotionEmoji.value = '❓';
    }

    // Gesture Detection (only if gestureRecognizer is available)
    if (gestureRecognizer) {
      const gestureResults = gestureRecognizer.recognizeForVideo(videoElement.value, startTimeMs);
      if (gestureResults.gestures && gestureResults.gestures.length > 0) {
        interpretGestures(gestureResults);
      } else {
        currentGesture.value = 'None';
      }
    }
    
  } catch (error) {
    console.error('Error during AI detection:', error);
  }

  // Continue loop
  animationFrameId = requestAnimationFrame(predictWebcam);
};

// 4. Interpret expressions from blend shapes
const interpretExpression = (blendshapes) => {
  // Extract relevant blend shape scores
  const smileLeft = blendshapes.find(shape => shape.categoryName === 'mouthSmileLeft')?.score || 0;
  const smileRight = blendshapes.find(shape => shape.categoryName === 'mouthSmileRight')?.score || 0;
  const jawOpen = blendshapes.find(shape => shape.categoryName === 'jawOpen')?.score || 0;
  const eyeBlinkLeft = blendshapes.find(shape => shape.categoryName === 'eyeBlinkLeft')?.score || 0;
  const eyeBlinkRight = blendshapes.find(shape => shape.categoryName === 'eyeBlinkRight')?.score || 0;
  
  // More blend shapes for better detection
  const browDownLeft = blendshapes.find(shape => shape.categoryName === 'browDownLeft')?.score || 0;
  const browDownRight = blendshapes.find(shape => shape.categoryName === 'browDownRight')?.score || 0;
  const browInnerUp = blendshapes.find(shape => shape.categoryName === 'browInnerUp')?.score || 0;
  const browOuterUpLeft = blendshapes.find(shape => shape.categoryName === 'browOuterUpLeft')?.score || 0;
  const browOuterUpRight = blendshapes.find(shape => shape.categoryName === 'browOuterUpRight')?.score || 0;
  
  const mouthFrownLeft = blendshapes.find(shape => shape.categoryName === 'mouthFrownLeft')?.score || 0;
  const mouthFrownRight = blendshapes.find(shape => shape.categoryName === 'mouthFrownRight')?.score || 0;
  const mouthPucker = blendshapes.find(shape => shape.categoryName === 'mouthPucker')?.score || 0;
  const mouthStretchLeft = blendshapes.find(shape => shape.categoryName === 'mouthStretchLeft')?.score || 0;
  const mouthStretchRight = blendshapes.find(shape => shape.categoryName === 'mouthStretchRight')?.score || 0;
  
  const eyeSquintLeft = blendshapes.find(shape => shape.categoryName === 'eyeSquintLeft')?.score || 0;
  const eyeSquintRight = blendshapes.find(shape => shape.categoryName === 'eyeSquintRight')?.score || 0;
  const eyeWideLeft = blendshapes.find(shape => shape.categoryName === 'eyeWideLeft')?.score || 0;
  const eyeWideRight = blendshapes.find(shape => shape.categoryName === 'eyeWideRight')?.score || 0;
  
  // Expression detection logic with HARDER THRESHOLDS (less sensitive)
  let detectedEmotion = 'Neutral';
  let confidence = 0;
  
  // Calculate average scores
  const avgSmile = (smileLeft + smileRight) / 2;
  const avgBrowDown = (browDownLeft + browDownRight) / 2;
  const avgBrowUp = (browOuterUpLeft + browOuterUpRight + browInnerUp) / 3;
  const avgFrown = (mouthFrownLeft + mouthFrownRight) / 2;
  const avgEyeWide = (eyeWideLeft + eyeWideRight) / 2;
  const avgEyeSquint = (eyeSquintLeft + eyeSquintRight) / 2;
  
  // Check if user is speaking (presentation mode)
  // If speaking, we suppress mouth-based emotions like Happy, Surprised, Sad
  const isSpeaking = currentVolume.value > 15; // Threshold for speaking
  
  // Priority 1: Blinking (highest priority, unaffected by speech)
  if (eyeBlinkLeft > 0.7 && eyeBlinkRight > 0.7) {
    detectedEmotion = 'Blinking';
    confidence = (eyeBlinkLeft + eyeBlinkRight) / 2;
  }
  // Priority 2: Surprised (wide eyes + open mouth)
  // HARDER THRESHOLD: Increased from 0.3 to 0.5
  // SPEECH CHECK: If speaking, require extreme wide eyes
  else if ((!isSpeaking && (jawOpen > 0.5 || (avgEyeWide > 0.5 && jawOpen > 0.3))) || 
           (isSpeaking && avgEyeWide > 0.8)) {
    detectedEmotion = 'Surprised';
    confidence = Math.max(jawOpen, avgEyeWide);
  }
  // Priority 3: Happy (smile detection)
  // HARDER THRESHOLD: Increased from 0.3 to 0.55
  // SPEECH CHECK: Suppressed if speaking (smiling while talking is common)
  else if (!isSpeaking && avgSmile > 0.55) {
    detectedEmotion = 'Happy';
    confidence = avgSmile;
  }
  // Priority 4: Angry (brow down + squint or frown)
  // HARDER THRESHOLD: Increased from 0.2 to 0.4
  // SPEECH CHECK: Allowed but harder (brows are key)
  else if (avgBrowDown > 0.4 || (avgEyeSquint > 0.5 && avgFrown > 0.3)) {
    detectedEmotion = 'Angry';
    confidence = Math.max(avgBrowDown, avgEyeSquint);
  }
  // Priority 5: Sad (frown + brow inner up)
  // HARDER THRESHOLD: Increased from 0.15/0.2 to 0.4
  // SPEECH CHECK: Suppressed if speaking
  else if (!isSpeaking && ((avgFrown > 0.4 && browInnerUp > 0.4) || (avgFrown > 0.5 && avgSmile < 0.1))) {
    detectedEmotion = 'Sad';
    confidence = Math.max((avgFrown + browInnerUp) / 2, avgFrown);
  }
  
  // Update UI
  currentExpression.value = detectedEmotion;
  emotionEmoji.value = emotionMap[detectedEmotion] || '😐';
  emotionSource.value = '📹'; // Camera source
  
  // 🆕 AUTO-MESSAGE FEATURE: Send hidden message when emotion is stable
  checkAndSendEmotionMessage(detectedEmotion, confidence);
};

// 🆕 Handle audio volume level
const currentVolume = ref(0);
const handleVolumeLevel = (level) => {
  currentVolume.value = level;
};

// 🆕 Handle audio emotion detection
const handleAudioEmotion = (audioData) => {
  console.log('🎤 Audio emotion:', audioData);
  
  // Update UI with audio-detected emotion (takes priority)
  currentExpression.value = audioData.emotion;
  emotionEmoji.value = emotionMap[audioData.emotion] || '😐';
  emotionSource.value = '🎤'; // Audio source
  
  // Audio emotions trigger immediately (no stability check needed)
  if (audioData.confidence > 0.7) {
    // Send message with audio context
    sendHiddenEmotionMessage(audioData.emotion, audioData);
  }
  
  // Reset to camera emotion after 3 seconds
  setTimeout(() => {
    emotionSource.value = '📹';
  }, 3000);
};

// 🆕 Function to check if we should send an auto-message based on emotion
const checkAndSendEmotionMessage = (emotion, confidence) => {
  // Only trigger for emotions with good confidence
  // HARDER THRESHOLD: Increased from 0.35 to 0.6
  if (confidence < 0.6) return;
  
  // Add to emotion history for stability check
  emotionHistory.push(emotion);
  // INCREASED STABILITY BUFFER: From 10 to 45 (~1.5 seconds at 30fps)
  const REQUIRED_HISTORY_SIZE = 45;
  
  if (emotionHistory.length > REQUIRED_HISTORY_SIZE) {
    emotionHistory.shift();
  }
  
  // Check if emotion is stable (same emotion for last N frames)
  const stableEmotion = emotionHistory.length >= REQUIRED_HISTORY_SIZE &&
                        emotionHistory.every(e => e === emotion);
  
  if (!stableEmotion) return;
  
  // Don't send if we already sent for this emotion recently
  if (lastEmotionSent === emotion) return;
  
  // Record this emotion as sent
  lastEmotionSent = emotion;
  emotionStartTime = Date.now();
  
  // Clear last emotion after 30 seconds (can trigger again)
  setTimeout(() => {
    if (lastEmotionSent === emotion) {
      lastEmotionSent = '';
    }
  }, 30000);
  
  // Send hidden message based on detected emotion
  sendHiddenEmotionMessage(emotion);
};

// 🆕 Send a hidden message to AI based on detected emotion
const sendHiddenEmotionMessage = (emotion, audioData = null) => {
  const emotionMessages = {
    'Happy': audioData 
      ? `The user just laughed out loud (said "${audioData.sound}")! Respond playfully and ask what's so funny.`
      : "[System Event: User is smiling warmly at you.] Notice their smile and ask what's making them happy today.",
    
    'Sad': audioData
      ? `The user sighed or made a sad sound. Show empathy and ask if they're okay.`
      : "[System Event: User looks sad or down.] Show concern and ask gently if everything is okay.",
    
    'Angry': audioData
      ? `The user expressed frustration verbally (said "${audioData.sound}"). Respond calmly and ask what's wrong.`
      : "[System Event: User looks frustrated/angry.] Respond calmly and ask what is bothering them.",
    
    'Surprised': audioData
      ? `The user just exclaimed in surprise (said "${audioData.sound}")! Ask them excitedly what happened.`
      : "[System Event: User looks surprised.] Ask them what happened or what caught their attention."
  };
  
  const message = emotionMessages[emotion];
  
  if (message) {
    const source = audioData ? '🎤 Audio' : '📹 Camera';
    console.log(`📤 Sending hidden emotion prompt (${source}): ${emotion}`);
    
    // Send message through WebSocket (won't appear in chat UI)
    websocketService.sendMessage({
      text: message,
      hidden: true  // Flag to indicate this shouldn't show in UI
    });
    
    // Show notification to user (optional)
    console.log(`💡 AI noticed you're ${emotion.toLowerCase()} (${source}) and will ask about it!`);
  }
};

// 🆕 Interpret Gestures
const interpretGestures = (results) => {
  const now = Date.now();
  
  // Check standard gestures from first recognized hand
  if (!results.gestures || results.gestures.length === 0) {
    currentGesture.value = 'None';
    return;
  }
  const gestureName = results.gestures[0][0].categoryName;
  const confidence = results.gestures[0][0].score;
  
  if (confidence < 0.6) return; // Ignore low confidence gestures
  
  switch(gestureName) {
    case 'Open_Palm':
      currentGesture.value = 'Open Palm';
      gestureIcon.value = '✋';
      if (now - lastGestureTime > GESTURE_COOLDOWN) {
        executeGestureAction('Stop AI', () => {
          console.log('✋ Gesture Triggered: Terminating AI Response');
          websocketService.terminateResponse();
          showToast('✋', 'AI response terminated');
        });
      }
      break;
      
    case 'Pointing_Up':
      currentGesture.value = 'Pointing Up';
      gestureIcon.value = '🤫';
      if (now - lastGestureTime > GESTURE_COOLDOWN) {
        executeGestureAction('Mute System', async () => {
          console.log('🤫 Gesture Triggered: Toggling System Mute');
          // Also pause AI audio locally
          if (websocketService.currentAudio) {
            websocketService.currentAudio.pause();
          }
          try {
            // Get current state first so we can show intent
            const statusRes = await fetch('http://localhost:8000/api/system/mute-status');
            const statusData = await statusRes.json();
            const willMute = !statusData.muted;
            showToast('🤫', willMute ? 'Muting system... 🔇' : 'Unmuting system... 🔊');

            // Toggle mute
            const res = await fetch('http://localhost:8000/api/system/toggle-mute', { method: 'POST' });
            const data = await res.json();
            if (res.ok) {
              showToast('🤫', data.muted ? 'System Muted 🔇' : 'System Unmuted 🔊', 3000);
            } else {
              showToast('⚠️', 'Mute failed: ' + data.detail);
            }
          } catch (err) {
            showToast('⚠️', 'Cannot reach backend');
          }
        });
      }
      break;
      
    case 'Victory':
      currentGesture.value = 'Victory';
      gestureIcon.value = '✌️';
      if (now - lastGestureTime > GESTURE_COOLDOWN) {
        executeGestureAction('Take Screenshot', async () => {
          console.log('✌️ Gesture Triggered: Taking Screenshot');
          showToast('✌️', 'Capturing screenshot...');
          await takeAndUploadScreenshot();
        });
      }
      break;
      
    case 'Closed_Fist':
      currentGesture.value = 'Closed Fist';
      gestureIcon.value = '👊';
      if (now - lastGestureTime > GESTURE_COOLDOWN) {
        executeGestureAction('Close Tab', async () => {
          console.log('👊 Gesture Triggered: Close Tab via backend Ctrl+W');
          showToast('👊', 'Closing tab...');
          try {
            await fetch('http://localhost:8000/api/system/close-tab', { method: 'POST' });
          } catch (e) {
            // Error expected because tab is closing
          }
        });
      }
      break;
      
    default:
      currentGesture.value = gestureName;
      gestureIcon.value = '🖐️'; // Default
      break;
  }
};

const executeGestureAction = (actionName, actionFn) => {
  lastGestureTime = Date.now();
  gestureAction.value = actionName;
  
  // Clear action text after 2 seconds
  setTimeout(() => {
    if (gestureAction.value === actionName) {
      gestureAction.value = '';
    }
  }, 2000);
  
  actionFn();
};

const takeAndUploadScreenshot = async () => {
  try {
    gestureAction.value = 'Capturing...';
    
    try {
      // 1. Trigger the screenshot FIRST before any visual effects
      const response = await fetch('http://localhost:8000/api/system/screenshot', { method: 'POST' });
      const data = await response.json();
      
      // 2. THEN trigger the flash / sound effect so it isn't captured in the image
      triggerShutterEffect();
      
      if (response.ok) {
        gestureAction.value = 'Screenshot Saved!';
        showToast('✅', 'Saved to system and pdf_uploads');
        console.log('✅ Screenshot captured and copied server-side.');
      } else {
        gestureAction.value = 'Capture Failed';
        showToast('❌', 'Backend screenshot failed: ' + data.detail);
      }
    } catch (err) {
      console.error('Screenshot Request Error', err);
      gestureAction.value = 'Request Error';
      showToast('❌', 'Error reaching server: ' + err.message);
    }
    
  } catch (error) {
    console.error('Screenshot error:', error);
    gestureAction.value = 'Capture Error';
    showToast('❌', 'Failed to trigger screenshot sequence');
  }
};

// Toggle camera function
const toggleCamera = async () => {
  if (cameraActive.value) {
    stopCamera();
  } else {
    isLoading.value = true;
    
    // Initialize AI models if not already done
    if (!faceLandmarker || !gestureRecognizer) {
      const success = await initAIModels();
      if (!success) {
        isLoading.value = false;
        return;
      }
    }
    
    // Enable camera
    await enableCam();
    isLoading.value = false;
  }
};

// Stop camera function
const stopCamera = () => {
  // Stop animation loop
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }
  
  // Stop camera stream
  if (videoElement.value && videoElement.value.srcObject) {
    const tracks = videoElement.value.srcObject.getTracks();
    tracks.forEach(track => track.stop());
    videoElement.value.srcObject = null;
  }
  
  cameraActive.value = false;
  faceDetected.value = false;
  currentExpression.value = 'Neutral';
  emotionEmoji.value = '😐';
  
  console.log('🛑 Camera stopped');
};

// --- Vue Lifecycle Hooks ---

onMounted(async () => {
  console.log('📷 Camera component mounted');
  // Optionally auto-start camera (uncomment if needed)
  // await toggleCamera();
});

onBeforeUnmount(() => {
  console.log('🧹 Cleaning up camera component');
  stopCamera();
});
</script>

<style scoped>
.camera-view {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: rgba(10, 12, 22, 0.8);
  overflow: hidden;
  clip-path: polygon(
    0 0, 
    100% 0, 
    100% calc(100% - 20px), 
    calc(100% - 20px) 100%, 
    0 100%
  );
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 246, 255, 0.3);
  border: 1px solid rgba(0, 246, 255, 0.3);
}

.camera-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  z-index: 10;
  background: linear-gradient(135deg, rgba(10, 12, 22, 0.8) 0%, rgba(20, 24, 44, 0.7) 100%);
  backdrop-filter: blur(4px);
}

.camera-text {
  font-family: var(--font-display);
  font-size: 1.5rem;
  margin-bottom: 1rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--color-accent-primary);
  text-shadow: 0 0 10px rgba(0, 246, 255, 0.6);
}

.camera-icon {
  margin-bottom: 1rem;
  opacity: 0.7;
  color: var(--color-accent-primary);
  filter: drop-shadow(0 0 5px rgba(0, 246, 255, 0.8));
}

@keyframes pulse {
  0% { opacity: 0.5; transform: scale(0.95); filter: drop-shadow(0 0 5px rgba(0, 246, 255, 0.4)); }
  50% { opacity: 1; transform: scale(1.05); filter: drop-shadow(0 0 15px rgba(0, 246, 255, 0.8)); }
  100% { opacity: 0.5; transform: scale(0.95); filter: drop-shadow(0 0 5px rgba(0, 246, 255, 0.4)); }
}

.pulse-animation {
  animation: pulse 2s infinite ease-in-out;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); /* Mirror the camera */
  display: none;
}

.camera-feed.active {
  display: block;
}

.emotion-overlay {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 20;
}

.emotion-badge {
  background-color: rgba(10, 12, 22, 0.9);
  border-radius: 0;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.5);
  border: 1px solid var(--color-accent-primary);
  clip-path: polygon(
    0 0,
    calc(100% - 10px) 0,
    100% 10px,
    100% 100%,
    10px 100%,
    0 calc(100% - 10px)
  );
  backdrop-filter: blur(10px);
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.emotion-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 5px rgba(0, 246, 255, 0.8));
}

.emotion-text {
  font-size: 1rem;
  font-weight: 600;
  font-family: var(--font-display);
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--color-accent-primary);
  text-shadow: 0 0 8px rgba(0, 246, 255, 0.8);
}

.emotion-source {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-left: 8px;
}

.gesture-badge {
  background-color: rgba(10, 12, 22, 0.9);
  border-radius: 0;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 0 20px rgba(217, 70, 239, 0.5); /* Purple tint */
  border: 1px solid #d946ef;
  clip-path: polygon(
    0 0,
    calc(100% - 10px) 0,
    100% 10px,
    100% 100%,
    10px 100%,
    0 calc(100% - 10px)
  );
  backdrop-filter: blur(10px);
  animation: slideInUp 0.5s ease-out;
}

.gesture-info {
  display: flex;
  flex-direction: column;
}

.gesture-action {
  font-size: 0.8rem;
  color: #d946ef;
  font-family: var(--font-body);
  margin-top: 4px;
}

.detection-status {
  background-color: rgba(10, 12, 22, 0.9);
  border: 1px solid rgba(255, 0, 0, 0.5);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  font-family: var(--font-body);
  color: #ff4444;
  text-transform: uppercase;
  letter-spacing: 1px;
  clip-path: polygon(
    0 0,
    calc(100% - 8px) 0,
    100% 8px,
    100% 100%,
    0 100%
  );
  width: fit-content;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.detection-status.face-detected {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.4);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ff4444;
  animation: blink 2s infinite;
}

.detection-status.face-detected .status-dot {
  background-color: var(--color-accent-primary);
  box-shadow: 0 0 10px var(--color-accent-primary);
  animation: breathe 2s infinite ease-in-out;
}

@keyframes blink {
  0%, 50%, 100% { opacity: 1; }
  25%, 75% { opacity: 0.3; }
}

@keyframes breathe {
  0%, 100% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
}

.stop-camera-btn {
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.5);
  color: #ff4444;
  padding: 8px 16px;
  font-family: var(--font-display);
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  clip-path: polygon(
    8px 0,
    100% 0,
    100% calc(100% - 8px),
    calc(100% - 8px) 100%,
    0 100%,
    0 8px
  );
  display: flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  backdrop-filter: blur(10px);
}

.stop-camera-btn:hover {
  background: rgba(255, 0, 0, 0.4);
  border-color: #ff4444;
  box-shadow: 0 0 15px rgba(255, 0, 0, 0.3);
  transform: translateX(3px);
}

.stop-camera-btn:active {
  transform: translateX(1px) scale(0.98);
}

.camera-status {
  margin-bottom: 1.5rem;
  opacity: 0.7;
  font-family: var(--font-body);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  position: relative;
  padding: 5px 10px;
  border: 1px solid rgba(0, 246, 255, 0.3);
  background: rgba(10, 12, 22, 0.6);
}

.camera-button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--color-accent-primary) 0%, var(--color-accent-tertiary) 100%);
  color: white;
  border: none;
  border-radius: 0;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(0, 246, 255, 0.3);
  font-family: var(--font-display);
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;
  clip-path: polygon(
    10px 0,
    100% 0,
    100% calc(100% - 10px),
    calc(100% - 10px) 100%,
    0 100%,
    0 10px
  );
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.camera-button::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, var(--color-accent-primary), var(--color-accent-tertiary));
  z-index: -1;
  filter: blur(10px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.camera-button:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-accent-tertiary) 0%, var(--color-accent-primary) 100%);
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.5);
}

.camera-button:hover:not(:disabled)::before {
  opacity: 1;
}

.camera-button:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3);
}

/* ====== Toast Notification ====== */
.gesture-toast {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(10, 12, 22, 0.95);
  border: 1px solid #d946ef;
  box-shadow: 0 0 20px rgba(217, 70, 239, 0.6);
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 50;
  white-space: nowrap;
  backdrop-filter: blur(10px);
  clip-path: polygon(
    8px 0,
    calc(100% - 8px) 0,
    100% 8px,
    100% calc(100% - 8px),
    calc(100% - 8px) 100%,
    8px 100%,
    0 calc(100% - 8px),
    0 8px
  );
}

.toast-icon {
  font-size: 1.3rem;
}

.toast-message {
  font-family: var(--font-display);
  font-size: 0.7rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #d946ef;
  text-shadow: 0 0 8px rgba(217, 70, 239, 0.8);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>