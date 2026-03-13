<template>
  <div class="character-view">
    <div ref="canvasContainer" class="canvas-container"></div>
    <div v-if="loadingModel" class="loading-overlay">
      <div class="loading-text">LOADING CHARACTER MODEL...</div>
    </div>
    
    <!-- Game-style dialogue box -->
    <div v-if="showDialogue && !hideDialogue" class="dialogue-box">
      <div class="dialogue-header">
        <div class="dialogue-avatar">
          <img src="/vite.svg" alt="AI Avatar" />
        </div>
        <div class="dialogue-title">AI ASSISTANT</div>
        <button @click="showDialogue = false" class="close-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="dialogue-content">
        <div class="dialogue-text">Hi, I'm your AI Assistant. Ready to chat?</div>
        <div class="text-cursor"></div>
      </div>
      
      <div class="dialogue-divider">
        <span>TRY ASKING ME:</span>
      </div>
      
      <div class="dialogue-options">
        <button @click="handleIntroduction" class="option-btn prompt-btn" style="animation-delay: 0.1s">
          <div class="option-highlight"></div>
          Tell me more about you
        </button>
        <button @click="sendMessage('Tell me a joke')" class="option-btn prompt-btn" style="animation-delay: 0.2s">
          <div class="option-highlight"></div>
          Tell me a joke
        </button>
        <button @click="sendMessage('Talk about the weather today')" class="option-btn prompt-btn" style="animation-delay: 0.3s">
          <div class="option-highlight"></div>
          Talk about the weather today
        </button>
        <button @click="sendMessage('What can you do?')" class="option-btn prompt-btn" style="animation-delay: 0.4s">
          <div class="option-highlight"></div>
          What can you do?
        </button>
      </div>
      
      <div class="dialogue-history">
        <div class="history-label">DIALOGUE HISTORY:</div>
        <div class="history-content">[User systems initialized...]
[Connection established...]</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineExpose, watch } from 'vue';
import { useRoute } from 'vue-router'; // Import useRoute
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { retargetClip, relaxArms } from '../../services/animationUtils';
import { useChatStore } from '../../stores/chatStore';
import { useUIStore } from '../../stores/uiStore';
import { websocketService } from '../../services/websocket';

const canvasContainer = ref(null);
const vrmRef = ref(null);
const loadingModel = ref(true);
const route = useRoute();
// If transition is present, hide dialogue initially, otherwise default to true
const showDialogue = ref(route.query.transition !== 'true'); 
const isTyping = ref(false);
const chatStore = useChatStore();
const uiStore = useUIStore();

// Props
const props = defineProps({
  hideDialogue: {
    type: Boolean,
    default: false
  }
});

// Watch messages to toggle dialogue visibility
watch(() => chatStore.messages.length, (newCount) => {
  // If there are messages, hide the welcome dialogue
  if (newCount > 0) {
    showDialogue.value = false;
  } else {
    // Only show if NOT coming from transition
    if (route.query.transition !== 'true') {
        showDialogue.value = true;
    }
  }
}, { immediate: true });

// Animation states
const wavingAction = ref(null);
const walkingAction = ref(null);
const hitAction = ref(null);
const idleAction = ref(null);
const hasWaved = ref(false);
let characterWrapperGroup = null; // Reference to the THREE.Group for rotation

let scene, camera, renderer, clock;
let mixer, currentAnimation;

// Function to set the expression on the VRM model
const setExpression = (name, weight = 1.0) => {
  if (!vrmRef.value || !vrmRef.value.expressionManager) {
    console.warn('Expression manager not available');
    return;
  }
  
  try {
    // Reset all expressions first (VRM v2.x API)
    const expressions = ['happy', 'sad', 'angry', 'surprised', 'neutral'];
    expressions.forEach(exp => {
      try {
        vrmRef.value.expressionManager.setValue(exp, 0);
      } catch (e) {
        // Expression might not exist, ignore
      }
    });
    
    // Set the requested expression
    vrmRef.value.expressionManager.setValue(name, weight);
    console.log(`Expression set: ${name} = ${weight}`);
  } catch (error) {
    console.warn(`Failed to set expression '${name}':`, error);
  }
};

// Initialize the Three.js scene
const initScene = () => {
  // Create scene, camera, and renderer
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(
    30,  // Increased FOV from 30 to 35 for slightly wider view
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    0.1,
    20
  );
  
  renderer = new THREE.WebGLRenderer({ 
    antialias: true,
    alpha: true  // Enable transparent background
  });
  
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  // PyQt6 supports full transparency!
  renderer.setClearColor(0x000000, 0);  // Transparent background
  canvasContainer.value.appendChild(renderer.domElement);
  
  // Configure camera - keep original settings
  camera.position.set(0, 3.0, 6.5);  // Original position
  camera.lookAt(new THREE.Vector3(0, 1.2, 0));  // Look at character center
  
  // ===== TASK 1: Professional Three-Point Lighting Setup =====
  
  // 1.2. Key Light (Main Light) - Creates highlights and defines shadows
  const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);  // Balanced intensity
  keyLight.position.set(1, 1.5, 2);
  scene.add(keyLight);
  console.log('✨ Key Light added at', keyLight.position, 'intensity:', keyLight.intensity);
  
  // 1.3. Fill Light (Ambient) - Softens shadows, prevents pure black
  const fillLight = new THREE.AmbientLight(0xffffff, 0.5);  // Moderate fill
  scene.add(fillLight);
  console.log('💡 Fill Light added with intensity:', fillLight.intensity);
  
  // 1.4. Rim Light (Backlight) - Creates edge highlight, separates from background
  const rimLight = new THREE.DirectionalLight(0x88aaff, 0.6);  // Subtle blue glow
  rimLight.position.set(-0.5, 1.5, -1.5);
  scene.add(rimLight);
  console.log('🔵 Rim Light added at', rimLight.position, 'intensity:', rimLight.intensity);
  
  // Add gentle front light for face visibility
  const frontLight = new THREE.DirectionalLight(0xffffff, 0.8);  // Gentle front light
  frontLight.position.set(0, 1.2, 3);
  scene.add(frontLight);
  console.log('🔆 Front Light added for face visibility');
  
  // Optional: Light helpers for debugging (commented out)
  // const keyLightHelper = new THREE.DirectionalLightHelper(keyLight, 1);
  // const rimLightHelper = new THREE.DirectionalLightHelper(rimLight, 1);
  // scene.add(keyLightHelper);
  // scene.add(rimLightHelper);
  
  // Create animation clock
  clock = new THREE.Clock();
  
  // Load the VRM model
  loadVRMModel();
  
  // Handle window resize
  window.addEventListener('resize', onWindowResize);
};

// Load the VRM model
const loadVRMModel = () => {
  loadingModel.value = true;
  
  // Create a GLTFLoader
  const loader = new GLTFLoader();
  
  // Register VRM loader plugin (v2.x API)
  loader.register((parser) => {
    return new VRMLoaderPlugin(parser);
  });
  
  console.log('Starting to load VRM model from: /avatar.vrm');
  
  // Load the model
  loader.load(
    '/avatar.vrm',
    (gltf) => {
      // Get the VRM model from gltf.userData.vrm (v2.x API)
      const vrm = gltf.userData.vrm;
      
      if (!vrm) {
        console.error('VRM model not found in loaded GLTF');
        loadingModel.value = false;
        return;
      }
      
      console.log('VRM model loaded successfully:', vrm);
      
      // Store the model reference
      vrmRef.value = vrm;
      
      // ===== NEW STRATEGY: Use THREE.Group as Wrapper =====
      
      // 1. Create a wrapper group for better control
      const characterWrapper = new THREE.Group();
      characterWrapper.name = 'characterWrapper';
      characterWrapperGroup = characterWrapper; // Store reference for rotation
      
      // 2. Parent the character to the wrapper
      characterWrapper.add(vrm.scene);
      
      // 3. Add the wrapper to the main scene
      scene.add(characterWrapper);
      
      // 4. Control transformations via the wrapper
      // Scale to make character bigger/smaller
      characterWrapper.scale.set(2.1, 2.1, 2.1);  // 50% larger - adjust this value to scale
      
      // Move wrapper UP to center the character in frame
      characterWrapper.position.y = -0.6;  // Moved up from -0.3 to 0.3
      
      console.log('📦 Character wrapper - Scale:', characterWrapper.scale.x, 'Position Y:', characterWrapper.position.y);
      
      // ===== TASK 2: Initialize Animation System =====
      
      // 2.1. Create AnimationMixer for the character
      mixer = new THREE.AnimationMixer(vrm.scene);
      console.log('🎬 AnimationMixer created');
      
      // Camera stays at fixed position - NO auto-adjustment
      // (Removed camera.lookAt head tracking to allow wrapper positioning to work)
      
      // Set default expression
      setExpression('neutral');
      
      // VRM models face +Z by default, so rotate it to face the camera (-Z)
      VRMUtils.rotateVRM0(vrm);
      
      // Relax arms immediately to avoid T-pose flash before animations load
      relaxArms(vrm);
      
      console.log('Rim light check - scene has', scene.children.length, 'children');
      
      loadingModel.value = false;
      
      console.log('✅ VRM Model loaded, preparing to load animations...');
      console.log('🎯 Step 1: Loading idle animation first...');
      
      // Load idle animation first (default pose)
      loadIdleAnimation();
      
      // Start the animation loop
      animate();
    },
    (progress) => {
      // Loading progress
      const percent = (progress.loaded / progress.total) * 100;
      console.log('Loading model:', percent.toFixed(2), '%');
    },
    (error) => {
      console.error('Error loading VRM model:', error);
      loadingModel.value = false;
    }
  );
};

// Load idle animation from FBX
const loadIdleAnimation = () => {
  const fbxLoader = new FBXLoader();
  
  console.log('🔍 Loading idle animation from /animations/Idle.fbx');
  
  fbxLoader.load(
    '/animations/Idle.fbx',
    (fbx) => {
      console.log('✅ FBX idle animation loaded successfully');
      
      if (fbx.animations && fbx.animations.length > 0) {
        // Retarget FBX animation to VRM skeleton + freeze legs
        const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });
        console.log('🎬 Idle animation retargeted, tracks:', retargetedClip.tracks.length);
        
        // Create and play idle animation immediately
        idleAction.value = mixer.clipAction(retargetedClip);
        idleAction.value.setLoop(THREE.LoopRepeat);
        idleAction.value.timeScale = 1.0;
        idleAction.value.play();
        
        console.log('▶️ Playing retargeted idle animation');
        
        // Now load all other animations
        loadWavingAnimation();
        loadWalkingAnimation();
        loadHitAnimation();
      } else {
        console.warn('⚠️ No animations found in idle.fbx file');
        // Still load waving animation even if idle fails
        loadWavingAnimation();
      }
    },
    (progress) => {
      const percent = (progress.loaded / progress.total) * 100;
      console.log(`📥 Idle FBX Loading: ${percent.toFixed(1)}%`);
    },
    (error) => {
      console.error('❌ Error loading idle animation:', error);
      // Still load other animations even if idle fails
      loadWavingAnimation();
      loadWalkingAnimation();
      loadHitAnimation();
    }
  );
};

// Load waving animation from FBX
const loadWavingAnimation = () => {
    const fbxLoader = new FBXLoader();
    fbxLoader.load('/animations/AvatarSample_A@Waving.fbx', (fbx) => {
        if (fbx.animations.length) {
            const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });
            wavingAction.value = mixer.clipAction(retargetedClip);
            wavingAction.value.setLoop(THREE.LoopRepeat);
            wavingAction.value.clampWhenFinished = false;
            wavingAction.value.timeScale = 0.4;
            console.log('✅ Waving animation loaded and retargeted');
        }
    });
};

// Load Walking Animation
const loadWalkingAnimation = () => {
  const fbxLoader = new FBXLoader();
  console.log('🔍 Loading walking animation...');
  fbxLoader.load('/animations/Brutal To Happy Walking.fbx', (fbx) => {
      if (fbx.animations.length) {
          const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });
          walkingAction.value = mixer.clipAction(retargetedClip);
          walkingAction.value.setLoop(THREE.LoopRepeat);
          console.log('✅ Walking animation loaded and retargeted');
      }
  });
};

// Load Hit Animation
const loadHitAnimation = () => {
  const fbxLoader = new FBXLoader();
  console.log('🔍 Loading hit animation...');
  fbxLoader.load('/animations/Hit On Side Of Body.fbx', (fbx) => {
      if (fbx.animations.length) {
          const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });
          hitAction.value = mixer.clipAction(retargetedClip);
          hitAction.value.setLoop(THREE.LoopOnce);
          hitAction.value.clampWhenFinished = true;
          console.log('✅ Hit animation loaded and retargeted');
      }
  });
};

// Play waving animation
const playWave = () => {
  if (!wavingAction.value) {
    console.log('⚠️ Cannot wave: animation not ready');
    return;
  }
  
  console.log('👋 Playing waving animation');
  
  // Set joy expression
  setExpression('joy', 1.0);
  
  // Fade out idle to prevent animation conflict
  if (idleAction.value) idleAction.value.fadeOut(0.3);
  
  // Fade in and play waving animation
  wavingAction.value.reset();
  wavingAction.value.fadeIn(0.3);
  wavingAction.value.play();
  
  // Stop after 10 seconds and return to idle
  setTimeout(() => {
    if (wavingAction.value) {
      wavingAction.value.fadeOut(0.5);
    }
    
    // Restart idle animation
    if (idleAction.value) {
      idleAction.value.reset();
      idleAction.value.fadeIn(0.5);
      idleAction.value.play();
    }
    
    setExpression('neutral');
    console.log('✅ Waving animation complete, returned to idle');
  }, 10000);
};

// Freeze legs during animations (only if original positions are saved)
const freezeLegs = () => {
  // REMOVED: freezeLegs was fighting the animation mixer every frame,
  // causing visual stutter and T-pose issues. Leg freezing is now handled
  // by filtering leg tracks during retargetClip() instead.
};

// Handle window resize
const onWindowResize = () => {
  if (!canvasContainer.value) return;
  
  camera.aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
};

// Animation loop
const animate = () => {
  requestAnimationFrame(animate);
  
  const delta = clock.getDelta();
  
  // Update animation mixer FIRST, then VRM
  if (mixer) {
    mixer.update(delta);
  }
  
  // After mixer applies animation, lock hips Y-rotation to prevent
  // root motion turning that causes snap on loop
  if (vrmRef.value && vrmRef.value.humanoid) {
    const hipsNode = vrmRef.value.humanoid.getNormalizedBoneNode('hips');
    if (hipsNode) {
      const euler = new THREE.Euler().setFromQuaternion(hipsNode.quaternion, 'YXZ');
      euler.y = 0; // Strip Y-axis turning
      hipsNode.quaternion.setFromEuler(euler);
    }
  }
  
  // Update VRM model (transfers normalized → raw bones, updates spring bones etc.)
  if (vrmRef.value) {
    vrmRef.value.update(delta);
  }
  
  // Render the scene
  renderer.render(scene, camera);
};

// Initialize when mounted
onMounted(() => {
  if (canvasContainer.value) {
    initScene();
  }
});

// Function to send a message when an option is clicked
const sendMessage = (text) => {
  isTyping.value = true;
  chatStore.sendMessage(text);
  
  // Send the message through the WebSocket service
  websocketService.sendMessage({
    text: text
  });
  
  // Close the dialogue after sending a message
  showDialogue.value = false;
  
  // Show the dialogue ticker
  uiStore.setDialogueTickerVisibility(true);
  
  // Reset typing state
  setTimeout(() => {
    isTyping.value = false;
  }, 300);
};

// Handle introduction button - trigger wave and send message
const handleIntroduction = () => {
  // Trigger waving animation
  playWave();
  
  // Send introduction message
  const introMessage = "Tell me more about you";
  isTyping.value = true;
  chatStore.sendMessage(introMessage);
  
  // Send through WebSocket
  websocketService.sendMessage({
    text: introMessage
  });
  
  // Close dialogue
  showDialogue.value = false;
  uiStore.setDialogueTickerVisibility(true);
  
  setTimeout(() => {
    isTyping.value = false;
  }, 300);
};

// Watch for typing events in the parent component
watch(isTyping, (isCurrentlyTyping) => {
  if (isCurrentlyTyping) {
    showDialogue.value = false;
  }
});

// Listen for chat input events
onMounted(() => {
  // Custom event to detect when user starts typing
  window.addEventListener('chat:typing', () => {
    showDialogue.value = false;
  });
  
  // Listen for character speaking event to trigger animations based on content
  window.addEventListener('character:speak', (event) => {
    const text = event.detail.text || '';
    
    // Check if the text mimics an introduction or greeting to trigger wave
    // Keywords: Suzune, Horikita (her name)
    if (text.toLowerCase().includes('suzune') || 
        text.toLowerCase().includes('horikita') ||
        text.toLowerCase().includes("i'm suzune") ||
        text.toLowerCase().includes("my name is")) {
      console.log('👋 Detected introduction in speech, triggering wave animation');
      playWave();
    }
  });
});



// Lip sync state
let currentMouthValue = 0;

// Update lip sync - called from parent via lipsync:volume events
const updateLipSync = (volume) => {
  if (!vrmRef.value || !vrmRef.value.expressionManager) return;

  // Smooth transition (lerp) — open fast, close slow
  const lerpFactor = volume > currentMouthValue ? 0.5 : 0.2;
  currentMouthValue += (volume - currentMouthValue) * lerpFactor;

  // Clamp to valid range
  const v = Math.max(0, Math.min(1, currentMouthValue));

  // Layer multiple visemes for a more natural look:
  //  - 'aa' (wide open mouth)  → dominant at high volume
  //  - 'oh' (rounded mouth)    → medium volume
  //  - 'ih' (slight open)      → low volume
  const em = vrmRef.value.expressionManager;

  try {
    em.setValue('aa', Math.pow(v, 1.2));           // Primary: wide open
    em.setValue('oh', Math.sin(v * Math.PI) * 0.3); // Secondary: peaks at mid-volume
    em.setValue('ih', v > 0.05 ? 0.15 : 0);         // Tertiary: subtle when speaking
  } catch (e) {
    // Some VRM models may not have all visemes — fallback to aa only
    try { em.setValue('aa', v); } catch (_) { /* ignore */ }
  }
};

// Play Walking Animation
const playWalk = () => {
  if (!walkingAction.value) return;
  
  // Fade out others
  if (idleAction.value) idleAction.value.fadeOut(0.2);
  if (wavingAction.value) wavingAction.value.fadeOut(0.2);
  
  walkingAction.value.reset();
  walkingAction.value.fadeIn(0.2);
  walkingAction.value.play();
  setExpression('happy', 0.5); // Slight smile when walking
};

// Stop Walking (Return to Idle)
const stopWalk = () => {
  if (walkingAction.value) walkingAction.value.fadeOut(0.5);
  if (idleAction.value) {
    idleAction.value.reset();
    idleAction.value.fadeIn(0.5);
    idleAction.value.play();
  }
  setExpression('neutral');
};

// Play Hit Animation
const playHit = () => {
  if (!hitAction.value) return;
  
  // Fade out others
  if (idleAction.value) idleAction.value.fadeOut(0.1);
  if (walkingAction.value) walkingAction.value.fadeOut(0.1);
  
  hitAction.value.reset();
  hitAction.value.fadeIn(0.1);
  hitAction.value.play();
  
  // Set expression for interaction
  setExpression('surprised', 1.0);
  
  // Return to idle after animation matches duration (approx 2s usually)
  setTimeout(() => {
    if (hitAction.value) hitAction.value.fadeOut(0.5);
    if (idleAction.value) {
       idleAction.value.reset();
       idleAction.value.fadeIn(0.5);
       idleAction.value.play();
    }
    setExpression('neutral');
  }, 2000); // Adjust based on actual duration if needed
};

// Set character facing direction (for walking)
// 'left' = face left, 'right' = face right, 'front' = face camera
const setFacing = (direction) => {
  if (!characterWrapperGroup) return;
  
  // VRM is already rotated 180° by VRMUtils.rotateVRM0, so directions are:
  // Positive Y = character's visual left (screen right from camera view)
  // Negative Y = character's visual right (screen left from camera view)
  const targetY = direction === 'right' ? 0.6   // Turn to face screen-right
                 : direction === 'left' ? -0.6  // Turn to face screen-left
                 : 0;                           // Face camera (front)
  
  // Smooth rotation via lerp in animate loop would be ideal,
  // but for simplicity, tween manually
  const startY = characterWrapperGroup.rotation.y;
  const duration = 300; // ms
  const startTime = performance.now();
  
  const tweenRotation = (now) => {
    const t = Math.min((now - startTime) / duration, 1);
    characterWrapperGroup.rotation.y = startY + (targetY - startY) * t;
    if (t < 1) requestAnimationFrame(tweenRotation);
  };
  requestAnimationFrame(tweenRotation);
  console.log(`🔄 Facing: ${direction}`);
};

// Expose internal methods
defineExpose({
    updateLipSync,
    setExpression,
    playWave,
    playWalk,
    stopWalk,
    playHit,
    setFacing
});
</script>

<style scoped>
.character-view {
  position: relative;
  width: 100%;
  height: 100%;
  background: transparent;  /* TRANSPARENT! Let UI background show through */
  overflow: hidden;
  clip-path: polygon(
    0 0, 
    100% 0, 
    100% calc(100% - 20px), 
    calc(100% - 20px) 100%, 
    0 100%
  );
  border: 1px solid rgba(0, 246, 255, 0.3);
}

.canvas-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;  /* Middle layer - character appears on top of input box */
  pointer-events: none;  /* Allow clicks to pass through to UI elements */
}

.canvas-container canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* Removed gradient overlays - canvas is now fully transparent */

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, rgba(10, 12, 22, 0.9) 0%, rgba(20, 24, 44, 0.8) 100%);
  color: var(--color-accent-primary);
  font-size: 1.2rem;
  z-index: 10;
  backdrop-filter: blur(5px);
}

.loading-text {
  background-color: rgba(0, 0, 0, 0.5);
  padding: 1rem 2rem;
  border-radius: 0;
  font-family: var(--font-display);
  letter-spacing: 1px;
  text-transform: uppercase;
  border: 1px solid var(--color-accent-primary);
  box-shadow: 0 0 20px rgba(0, 246, 255, 0.4);
  position: relative;
  clip-path: polygon(
    0 0,
    calc(100% - 15px) 0,
    100% 15px,
    100% 100%,
    15px 100%,
    0 calc(100% - 15px)
  );
  animation: pulse-text 2s infinite alternate ease-in-out;
}

@keyframes pulse-text {
  0% { box-shadow: 0 0 10px rgba(0, 246, 255, 0.3); text-shadow: 0 0 5px rgba(0, 246, 255, 0.5); }
  100% { box-shadow: 0 0 20px rgba(0, 246, 255, 0.6); text-shadow: 0 0 10px rgba(0, 246, 255, 0.8); }
}

/* Game-style dialogue box styles */
.dialogue-box {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-width: 600px;
  background-color: rgba(17, 22, 35, 0.97);
  border: 1px solid var(--color-accent-primary);
  box-shadow: 0 0 30px rgba(0, 246, 255, 0.5), inset 0 0 10px rgba(0, 246, 255, 0.2);
  z-index: 50;
  display: flex;
  flex-direction: column;
  clip-path: polygon(
    0 0,
    100% 0,
    100% calc(100% - 15px),
    calc(100% - 15px) 100%,
    0 100%
  );
  animation: fadeIn 0.5s ease-out;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -40%); }
  to { opacity: 1; transform: translate(-50%, -50%); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Dialogue history styling */
.dialogue-history {
  padding: 15px;
  background-color: rgba(10, 12, 22, 0.8);
  border-top: 1px solid rgba(0, 246, 255, 0.2);
  font-family: var(--font-mono, 'Courier New', monospace);
  font-size: 0.75rem;
  color: rgba(0, 246, 255, 0.7);
  margin-top: 10px;
  max-height: 80px;
  overflow-y: auto;
}

.history-label {
  color: var(--color-accent-tertiary);
  margin-bottom: 5px;
  font-size: 0.7rem;
  letter-spacing: 1px;
}

.history-content {
  line-height: 1.4;
  opacity: 0.8;
  white-space: pre-line;
}

.dialogue-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background: linear-gradient(90deg, rgba(0, 246, 255, 0.3) 0%, rgba(123, 45, 255, 0.3) 100%);
  border-bottom: 1px solid rgba(0, 246, 255, 0.5);
  position: relative;
  overflow: hidden;
}

.dialogue-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 246, 255, 0.5), transparent);
  animation: shine 3s infinite;
  pointer-events: none;
}

@keyframes shine {
  0% { left: -100%; }
  50% { left: 200%; }
  100% { left: 200%; }
}

.dialogue-avatar {
  width: 30px;
  height: 30px;
  background: rgba(10, 12, 22, 0.8);
  border: 1px solid var(--color-accent-primary);
  border-radius: 0;
  margin-right: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.dialogue-avatar img {
  width: 70%;
  height: 70%;
  object-fit: contain;
  filter: drop-shadow(0 0 3px var(--color-accent-primary));
}

.dialogue-title {
  flex-grow: 1;
  font-family: var(--font-display);
  font-size: 0.9rem;
  letter-spacing: 2px;
  color: var(--color-accent-primary);
  text-shadow: 0 0 5px rgba(0, 246, 255, 0.5);
  text-transform: uppercase;
}

.close-btn {
  background: rgba(10, 12, 22, 0.7);
  border: 1px solid rgba(0, 246, 255, 0.3);
  width: 22px;
  height: 22px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--color-accent-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  clip-path: polygon(
    0 0,
    100% 0,
    100% 100%,
    0 100%
  );
}

.close-btn:hover {
  background-color: rgba(0, 246, 255, 0.2);
  box-shadow: 0 0 8px rgba(0, 246, 255, 0.5);
  transform: scale(1.1);
}

.dialogue-content {
  padding: 20px;
  font-family: var(--font-body);
  color: var(--color-text-primary);
  font-size: 1.1rem;
  line-height: 1.5;
  text-align: center;
  letter-spacing: 0.5px;
  position: relative;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 12, 20, 0.3);
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
}

.dialogue-text {
  position: relative;
  text-shadow: 0 0 10px rgba(0, 246, 255, 0.5);
}

.text-cursor {
  display: inline-block;
  width: 10px;
  height: 18px;
  background-color: var(--color-accent-primary);
  margin-left: 5px;
  animation: blinkCursor 1.2s infinite;
}

@keyframes blinkCursor {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

/* Dialogue divider */
.dialogue-divider {
  padding: 10px 0;
  text-align: center;
  position: relative;
  margin: 10px 0 0;
}

.dialogue-divider::before, .dialogue-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  height: 1px;
  width: calc(50% - 100px);
  background: linear-gradient(to right, transparent, var(--color-accent-primary));
}

.dialogue-divider::before {
  left: 10px;
}

.dialogue-divider::after {
  right: 10px;
  background: linear-gradient(to left, transparent, var(--color-accent-primary));
}

.dialogue-divider span {
  font-family: var(--font-display);
  font-size: 0.8rem;
  color: var(--color-accent-primary);
  background-color: rgba(17, 22, 35, 0.97);
  padding: 0 15px;
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
  z-index: 1;
  text-shadow: 0 0 10px rgba(0, 246, 255, 0.5);
}

/* Options styling */
.dialogue-options {
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-btn {
  text-align: left;
  padding: 10px 15px;
  background: rgba(10, 12, 22, 0.7);
  border: 1px solid rgba(0, 246, 255, 0.2);
  font-family: var(--font-body);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  clip-path: polygon(
    0 0,
    calc(100% - 10px) 0,
    100% 10px,
    100% 100%,
    0 100%
  );
  position: relative;
  overflow: hidden;
}

.option-highlight {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: var(--color-accent-primary);
  transform: scaleY(0);
  transition: transform 0.3s ease, width 0.3s ease;
  transform-origin: top;
}

.option-btn:hover {
  background: rgba(0, 246, 255, 0.1);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.3), inset 0 0 15px rgba(0, 246, 255, 0.1);
  transform: translateX(5px);
}

.option-btn:hover .option-highlight {
  transform: scaleY(1);
  width: 5px;
  box-shadow: 0 0 10px rgba(0, 246, 255, 0.8);
}

.option-btn:hover::before {
  content: '>';
  position: absolute;
  left: 10px;
  color: var(--color-accent-primary);
  opacity: 0;
  animation: fadeInArrow 0.3s forwards 0.1s;
}

@keyframes fadeInArrow {
  from { opacity: 0; left: 5px; }
  to { opacity: 1; left: 10px; }
}

.option-btn:hover {
  padding-left: 25px;
}

/* Prompt button animation */
.prompt-btn {
  animation: fadeInUp 0.5s ease-out forwards;
  animation-fill-mode: both;
  opacity: 0;
}
</style>