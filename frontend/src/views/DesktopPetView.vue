<template>
  <div class="desktop-pet-container">
    <div ref="canvasContainer" class="canvas-wrapper"></div>
    
    <!-- Chat Dialog (appears on double-click) -->
    <transition name="chat-slide">
      <div v-if="showChatDialog" class="chat-dialog">
        <div class="chat-dialog-inner">
          <div class="chat-input-wrapper">
            <input
              ref="chatInputRef"
              v-model="chatInput"
              type="text"
              class="chat-input"
              placeholder="Type a command..."
              @keydown.enter="sendChatMessage"
              @keydown.escape="closeChatDialog"
            />
            <button class="chat-send-btn" @click="sendChatMessage" :disabled="!chatInput.trim()">Send</button>
            <button class="chat-close-btn" @click="closeChatDialog">✕</button>
          </div>
          <div v-if="chatResponse" class="chat-response">
            <span class="response-label">AI:</span> {{ chatResponse }}
          </div>
        </div>
      </div>
    </transition>

    <!-- Toast Notification -->
    <div v-if="showToast" class="toast" :class="toastType">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { retargetClip, relaxArms, createClickBoundingBox } from '../services/animationUtils';
import { websocketService } from '../services/websocket';
import { useChatStore } from '../stores/chatStore';
import { useConversationStore } from '../stores/conversationStore';

const chatStore = useChatStore();
const conversationStore = useConversationStore();

const canvasContainer = ref(null);
const vrmRef = ref(null);
const loadingModel = ref(true);

// Chat dialog states
const showChatDialog = ref(false);
const chatInput = ref('');
const chatResponse = ref('');
const chatInputRef = ref(null);

// Voice input states
const isListening = ref(false);
const hasError = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('info');
let recognition = null;
let autoSendTimer = null;

// Animation states
const walkingAction = ref(null);
const idleAction = ref(null);
const wavingAction = ref(null);
const isInteracting = ref(false); // Flag to pause random movement
let characterWrapperGroup = null;
let clickBoundingBox = null; // Invisible box for fast click detection

// Cached raycaster (avoid creating new objects on every click)
const raycaster = new THREE.Raycaster();
const mouseVec = new THREE.Vector2();

let scene, camera, renderer, clock;
let mixer;
let animationFrameId;

// WebSocket connection for position updates
let ws = null;
let lastUpdateTime = 0;
const UPDATE_INTERVAL = 33; // ~30fps (1000ms / 30 = 33ms)

// --- Natural Movement State ---
const movementState = {
  isMoving: false,        // Is currently walking?
  isRotating: false,      // Is currently turning?
  interactionRotating: false, // Rotating to face front for interaction
  direction: 1,           // 1 = Right, -1 = Left
  targetRotation: 0,      // Desired Y rotation
  walkSpeed: 1.2,         // Walking speed
  rotationSpeed: 5.0,     // Speed of turning
  interactionRotSpeed: 4.0, // Smooth rotation speed for interaction turn
  
  // Bounds (will be updated on resize/init)
  bounds: {
    minX: -6, maxX: 6,
    groundY: -1.2 // Fixed Y position (adjust based on model size/camera)
  }
};

let decisionTimeout = null;

// Update bounds based on camera
const updateBounds = () => {
    if (!camera) return;
    const dist = camera.position.z; 
    const vFOV = THREE.MathUtils.degToRad(camera.fov);
    const height = 2 * Math.tan(vFOV / 2) * dist;
    const width = height * camera.aspect;
    
    // Padding to keep character inside screen
    const padding = 0.8; 
    movementState.bounds.minX = -width / 2 + padding;
    movementState.bounds.maxX = width / 2 - padding;
    
    // Ground Y position - fixed at bottom
    // Camera is at Y=1.4, looking at Y=0.8.
    // We want feet at bottom of view.
    // Let's stick to a fixed Y for now or calculate bottom of frustum.
    // Ideally, just keep existing groundY or tweak it.
    movementState.bounds.groundY = -height / 2 + 0.5; // Offset up slightly 
    
    if (characterWrapperGroup) {
        characterWrapperGroup.position.y = movementState.bounds.groundY;
    }
};

// --- Decision Logic (The "Brain") ---
const decideNextAction = () => {
    if (isInteracting.value) return; // Don't decide if interacting

    // 20% Idle, 80% Walk (More active movement)
    const isIdle = Math.random() < 0.2;
    
    if (isIdle) {
        // Stay Idle
        stopWalking();

        // Face the camera (Rotation Y = 0 or Math.PI depending on model)
        // Standard VRM/GLTF: 0 faces +Z (Camera).
        movementState.targetRotation = 0; 
        movementState.isRotating = true;
        
        // Wait 10-30 seconds
        const waitTime = (Math.random() * 20000) + 10000;
        decisionTimeout = setTimeout(decideNextAction, waitTime);
    } else {
        // Start Walking
        startWalkingSequence();
    }
};

const startWalkingSequence = () => {
    if (!characterWrapperGroup) return;

    // Pick a direction
    // If near Left edge, go Right. If near Right edge, go Left.
    // Otherwise random.
    const currentX = characterWrapperGroup.position.x;
    const { minX, maxX } = movementState.bounds;
    const edgeThreshold = 1.0;
    
    let direction = Math.random() < 0.5 ? 1 : -1;
    
    if (currentX < minX + edgeThreshold) direction = 1; // Force Right
    if (currentX > maxX - edgeThreshold) direction = -1; // Force Left
    
    movementState.direction = direction;
    
    // Determine Rotation
    // Standard VRM faces +Z. 
    // Moving Right (+X) -> Rotate -90 deg (or +270) -> Face +X? 
    // Wait, let's calibrate rotation.
    // Usually: 
    // Rotation Y = PI/2 (90 deg) -> Faces Left (-X) in some coordinate systems?
    // Let's assume:
    // Face Right (+X): Rotation Y = Math.PI / 2
    // Face Left (-X): Rotation Y = -Math.PI / 2
    
    movementState.targetRotation = direction === 1 ? Math.PI / 2 : -Math.PI / 2;
    
    // Start Rotation Phase
    movementState.isRotating = true;
    movementState.isMoving = false;
    
    // Switch to Idle animation during turn (optional, or walk)
    // Actually, usually turn in place is Idle or Turn anim. We'll use Idle.
    if (idleAction.value && walkingAction.value) {
        walkingAction.value.stop();
        idleAction.value.play();
    }
};

const stopWalking = () => {
    movementState.isMoving = false;
    movementState.isRotating = false;
    
    if (walkingAction.value) walkingAction.value.stop();
    if (idleAction.value) idleAction.value.play();
};

const updateMovement = (delta) => {
    if (!characterWrapperGroup) return;
    
    // 0. Handle Interaction Rotation (highest priority — turning to face camera before wave)
    if (movementState.interactionRotating) {
        const currentRot = characterWrapperGroup.rotation.y;
        const targetRot = 0; // Face front
        
        let diff = targetRot - currentRot;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        
        if (Math.abs(diff) < 0.03) {
            // Rotation complete — snap and play wave
            characterWrapperGroup.rotation.y = 0;
            movementState.interactionRotating = false;
            playWaveAnimation();
        } else {
            // Smooth ease-out rotation
            const step = movementState.interactionRotSpeed * delta;
            characterWrapperGroup.rotation.y += Math.sign(diff) * Math.min(Math.abs(diff), step);
        }
        return; // Don't do anything else while interaction-rotating
    }
    
    // 1. Handle Normal Rotation (walking turns)
    if (movementState.isRotating) {
        const currentRot = characterWrapperGroup.rotation.y;
        const targetRot = movementState.targetRotation;
        
        let diff = targetRot - currentRot;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        
        if (Math.abs(diff) < 0.05) {
            characterWrapperGroup.rotation.y = targetRot;
            movementState.isRotating = false;
            
            const isWalkingRot = Math.abs(Math.abs(targetRot) - Math.PI/2) < 0.1;
            
            if (isWalkingRot) {
                movementState.isMoving = true;
                
                if (idleAction.value) idleAction.value.stop();
                if (walkingAction.value) walkingAction.value.play();
                
                const walkDuration = (Math.random() * 2000) + 3000;
                decisionTimeout = setTimeout(() => {
                    stopWalking();
                    const nextWait = (Math.random() * 2000) + 1000; 
                    decisionTimeout = setTimeout(decideNextAction, nextWait);
                }, walkDuration);
            }
        } else {
            const step = movementState.rotationSpeed * delta;
            characterWrapperGroup.rotation.y += Math.sign(diff) * Math.min(Math.abs(diff), step);
        }
        return;
    }
    
    // 2. Handle Walking
    if (movementState.isMoving) {
        const moveStep = movementState.walkSpeed * delta * movementState.direction;
        const newX = characterWrapperGroup.position.x + moveStep;
        
        if (newX < movementState.bounds.minX || newX > movementState.bounds.maxX) {
            stopWalking();
            clearTimeout(decisionTimeout);
            decisionTimeout = setTimeout(decideNextAction, 1000); 
        } else {
            characterWrapperGroup.position.x = newX;
        }
    }
};

// Send character position to backend via WebSocket
const sendPositionUpdate = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN || !characterWrapperGroup || !camera) {
        return;
    }
    
    // Throttle updates to ~30fps
    const now = Date.now();
    if (now - lastUpdateTime < UPDATE_INTERVAL) {
        return;
    }
    lastUpdateTime = now;
    
    // Get character world position
    const worldPos = new THREE.Vector3();
    characterWrapperGroup.getWorldPosition(worldPos);
    
    // Project to screen coordinates
    const screenPos = worldPos.clone();
    screenPos.project(camera);
    
    // Convert from normalized device coordinates (-1 to 1) to screen pixels
    const x = (screenPos.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-(screenPos.y * 0.5) + 0.5) * window.innerHeight;
    
    // Estimate character size in screen space
    // We'll use a fixed size for now (can be improved by projecting bounding box)
    const characterWidth = 200;
    const characterHeight = 450; // Increased to ensure head isn't clipped
    
    // Adjust Y position UP slightly so mask includes the head
    const adjustedY = y - 50; // Offset UP by 50px (negative = up in screen coords)
    
    // Send to backend
    try {
        ws.send(JSON.stringify({
            x: Math.round(x),
            y: Math.round(adjustedY),
            width: characterWidth,
            height: characterHeight
        }));
    } catch (error) {
        console.error('Failed to send position update:', error);
    }
};

const loadIdleAnimation = () => {
  const loader = new FBXLoader();
  loader.load('/animations/Idle.fbx', (fbx) => {
    if (fbx.animations.length) {
      // Retarget FBX animation to VRM skeleton + filter legs
      const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });

      idleAction.value = mixer.clipAction(retargetedClip);
      idleAction.value.setLoop(THREE.LoopRepeat);
      idleAction.value.play();
    }
  });
};

const loadWalkingAnimation = () => {
  const loader = new FBXLoader();
  loader.load('/animations/Brutal To Happy Walking.fbx', (fbx) => {
    if (fbx.animations.length) {
      const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value);
      walkingAction.value = mixer.clipAction(retargetedClip);
      walkingAction.value.setLoop(THREE.LoopRepeat);
      walkingAction.value.play(); // Play immediately!
      
      // Stop idle if walking starts
      if (idleAction.value) {
        idleAction.value.stop();
      }
    }
  });
};

const loadWavingAnimation = () => {
  const loader = new FBXLoader();
  loader.load('/animations/AvatarSample_A@Waving.fbx', (fbx) => {
    if (fbx.animations.length) {
      const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });
      wavingAction.value = mixer.clipAction(retargetedClip);
      wavingAction.value.setLoop(THREE.LoopRepeat); // Repeat wave for longer duration
      wavingAction.value.clampWhenFinished = false;
      wavingAction.value.timeScale = 0.6; // Slow down to 60% speed
      
      console.log('Wave animation loaded and retargeted successfully');
    }
  }, undefined, (error) => {
    console.error('Failed to load wave animation:', error);
  });
};

const leftTurnAction = ref(null);
const rightTurnAction = ref(null);

// Load Turn Animations
const loadTurnAnimations = () => {
    const loader = new FBXLoader();
    
    // Load Left Turn
    loader.load('/animations/Left Turn.fbx', (fbx) => {
        if (fbx.animations.length) {
            const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value);
            leftTurnAction.value = mixer.clipAction(retargetedClip);
            leftTurnAction.value.setLoop(THREE.LoopOnce);
            leftTurnAction.value.clampWhenFinished = true;
            console.log('Left Turn animation loaded and retargeted');
        }
    });
    
    // Load Right Turn
    loader.load('/animations/Right Turn.fbx', (fbx) => {
        if (fbx.animations.length) {
            const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value);
            rightTurnAction.value = mixer.clipAction(retargetedClip);
            rightTurnAction.value.setLoop(THREE.LoopOnce);
            rightTurnAction.value.clampWhenFinished = true;
            console.log('Right Turn animation loaded and retargeted');
        }
    });
};

const triggerWaveInteraction = () => {
    if (isInteracting.value || !wavingAction.value) return;
    
    isInteracting.value = true;
    console.log("Starting Wave Interaction with Turn");
    
    // Stop ALL current movement & scheduled decisions
    clearTimeout(decisionTimeout);
    movementState.isMoving = false;
    movementState.isRotating = false;
    movementState.interactionRotating = false;
    
    // Stop walking (fade out)
    if (walkingAction.value) walkingAction.value.fadeOut(0.2);
    
    // KEY FIX: DO NOT stop Idle animation completely. 
    // Just fade it slightly or keep it. This prevents T-pose if Turn animation is invalid.
    if (idleAction.value && !idleAction.value.isRunning()) {
        idleAction.value.play();
    }
    
    // Determine Turn Direction and play animation
    if (characterWrapperGroup) {
        const currentRot = characterWrapperGroup.rotation.y;
        
        let diff = 0 - currentRot;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        
        // If already facing front, just wave immediately
        if (Math.abs(diff) < 0.1) {
             characterWrapperGroup.rotation.y = 0;
             playWaveAnimation();
             return; // CRITICAL: prevent fall-through to turn logic
        }
        
        // Walking RIGHT (rot=PI/2) → needs Left Turn to face camera
        // Walking LEFT (rot=-PI/2) → needs Right Turn to face camera
        const isLeftTurn = diff < 0;
        const turnAction = isLeftTurn ? leftTurnAction.value : rightTurnAction.value;
        const turnName = isLeftTurn ? "Left" : "Right";
        
        if (turnAction) {
            console.log(`Playing ${turnName} Turn animation. Diff: ${diff.toFixed(2)}`);
            
            // Fade out walking, keep idle as safety net
            if (walkingAction.value && walkingAction.value.isRunning()) walkingAction.value.fadeOut(0.3);
            
            // Hard reset turn action
            turnAction.reset();
            turnAction.setLoop(THREE.LoopOnce);
            turnAction.clampWhenFinished = true;
            turnAction.timeScale = 0.8; // Slow down turn slightly for smoother feel
            
            // Crossfade: Fade in Turn, Fade out Idle
            if (idleAction.value && idleAction.value.isRunning()) idleAction.value.fadeOut(0.3);
            turnAction.fadeIn(0.3);
            turnAction.play();
            
            // Smoothly rotate the wrapper in sync with the turn animation duration
            const turnDuration = (turnAction.getClip().duration / turnAction.timeScale) * 1000; // ms
            const startRot = currentRot;
            const startTime = performance.now();
            
            const animateWrapperRotation = () => {
                const elapsed = performance.now() - startTime;
                const progress = Math.min(elapsed / turnDuration, 1);
                // Ease-in-out for natural feel
                const ease = progress < 0.5 
                    ? 2 * progress * progress 
                    : 1 - Math.pow(-2 * progress + 2, 2) / 2;
                
                characterWrapperGroup.rotation.y = startRot + (diff * ease);
                
                if (progress < 1 && isInteracting.value) {
                    requestAnimationFrame(animateWrapperRotation);
                }
            };
            requestAnimationFrame(animateWrapperRotation);
            
            // Helper to clean up and transition to wave
            let turnHandled = false;
            const finishTurn = () => {
                if (turnHandled) return; // Prevent double-fire
                turnHandled = true;
                console.log("Turn finished. Starting wave.");
                turnAction.fadeOut(0.3);
                characterWrapperGroup.rotation.y = 0; // Ensure snapped
                playWaveAnimation();
            };
            
            // Listen for animation finish
            const onTurnFinished = (e) => {
                if (e.action === turnAction) {
                    mixer.removeEventListener('finished', onTurnFinished);
                    finishTurn();
                }
            };
            mixer.addEventListener('finished', onTurnFinished);
            
            // Backup Timeout — always fire wave if turn didn't trigger it
            setTimeout(() => {
                mixer.removeEventListener('finished', onTurnFinished);
                finishTurn();
            }, turnDuration + 300);
            
        } else {
            // Fallback: Code-driven rotation
            console.warn(`Turn ${turnName} animation missing. Using fallback.`);
            
            const startRot = currentRot;
            const startTime = Date.now();
            const duration = 300;
            
            const animateTurn = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = progress < 0.5 ? 2*progress*progress : 1-Math.pow(-2*progress+2, 2)/2;
                
                characterWrapperGroup.rotation.y = startRot + (diff * ease);
                
                if (progress < 1) {
                    requestAnimationFrame(animateTurn);
                } else {
                    characterWrapperGroup.rotation.y = 0;
                    playWaveAnimation();
                }
            };
            animateTurn();
        }
    } else {
        playWaveAnimation();
    }
};

const playWaveAnimation = () => {
    console.log("Playing wave animation");
    
    // Set happy expression
    if (vrmRef.value && vrmRef.value.expressionManager) {
        vrmRef.value.expressionManager.setValue('happy', 1.0);
    }
    
    // Fade out other animations with longer duration for smoothness
    if (walkingAction.value && walkingAction.value.isRunning()) walkingAction.value.fadeOut(0.4);
    if (idleAction.value && idleAction.value.isRunning()) idleAction.value.fadeOut(0.4);
    
    // Play wave animation with smooth fade-in
    wavingAction.value.reset();
    wavingAction.value.fadeIn(0.4);
    wavingAction.value.play();
    
    // Wave for 8 seconds then smoothly return to idle
    setTimeout(() => {
        if (wavingAction.value) wavingAction.value.fadeOut(0.6);
        if (idleAction.value) {
            idleAction.value.reset();
            idleAction.value.fadeIn(0.6);
            idleAction.value.play();
        }
        
        // Fade out happy expression
        if (vrmRef.value && vrmRef.value.expressionManager) {
            vrmRef.value.expressionManager.setValue('happy', 0.0);
        }
        
        isInteracting.value = false;
        
        // Idle for ~10 seconds before deciding next action
        decisionTimeout = setTimeout(decideNextAction, 10000);
        console.log("Wave complete → idle for 10s");
    }, 8000);
};

// Double-click detection for chat dialog
let lastClickTime = 0;
const DOUBLE_CLICK_THRESHOLD = 350; // ms

const onCanvasClick = (event) => {
    if (!vrmRef.value || !camera || !scene) return;
    
    // Reuse cached raycaster & mouse vector (no allocation per click)
    mouseVec.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouseVec.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouseVec, camera);
    
    // Use invisible bounding box for fast click detection
    if (clickBoundingBox) {
        const intersects = raycaster.intersectObject(clickBoundingBox);
        if (intersects.length > 0) {
            const now = Date.now();
            
            if (now - lastClickTime < DOUBLE_CLICK_THRESHOLD) {
                // Double-click → open chat dialog
                console.log('Model double-clicked! Opening chat dialog.');
                openChatDialog();
                lastClickTime = 0; // Reset to avoid triple-click
            } else {
                // Single click → wave
                lastClickTime = now;
                if (!isInteracting.value) {
                    // Delay wave slightly to detect double-click
                    setTimeout(() => {
                        if (lastClickTime !== 0 && Date.now() - lastClickTime >= DOUBLE_CLICK_THRESHOLD) {
                            console.log('Model single-clicked! Triggering wave.');
                            triggerWaveInteraction();
                        }
                    }, DOUBLE_CLICK_THRESHOLD);
                }
            }
        }
    }
};

// Chat dialog functions
const sendDialogMask = (visible) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (visible) {
        // Dialog is ~500px wide, ~80px tall, centered at bottom
        const dialogWidth = 550;
        const dialogHeight = 160;
        const dialogX = Math.round(window.innerWidth / 2);
        const dialogY = window.innerHeight - 30 - dialogHeight / 2; // bottom: 30px + half height
        ws.send(JSON.stringify({
            type: 'dialog_mask',
            visible: true,
            x: dialogX,
            y: Math.round(dialogY),
            width: dialogWidth,
            height: dialogHeight
        }));
    } else {
        ws.send(JSON.stringify({
            type: 'dialog_mask',
            visible: false
        }));
    }
};


const openChatDialog = async () => {
    console.log('🎯 Opening chat dialog - creating new conversation...');
    
    // Create a new conversation automatically
    const newConv = await conversationStore.createConversation('New Chat');
    console.log('✅ New conversation created:', newConv);
    
    // Tell backend to use this new conversation
    if (newConv && newConv.id) {
        if (websocketService.socket && websocketService.isConnected) {
            // 1. Tell backend to switch to this conversation
            websocketService.socket.send(JSON.stringify({
                type: 'restore_conversation',
                conversation_id: newConv.id
            }));
            console.log('🔄 Sent restore_conversation to backend:', newConv.id);
            
            // 2. Notify other clients (Web UI) about new conversation
            websocketService.socket.send(JSON.stringify({
                type: 'conversation_created',
                conversation_id: newConv.id,
                conversation_title: newConv.title,
                source: 'desktop_pet'
            }));
            console.log('📢 Notified other clients about new conversation:', newConv.id);
        } else {
            console.warn('⚠️ WebSocket not connected, cannot restore conversation');
        }
    } else {
        console.error('❌ Failed to create new conversation');
    }
    
    // Clear chat messages for fresh start
    chatStore.clearMessages();
    console.log('🧹 Cleared chat messages');
    
    showChatDialog.value = true;
    chatResponse.value = '';
    sendDialogMask(true);
    nextTick(() => {
        if (chatInputRef.value) chatInputRef.value.focus();
    });
};

const closeChatDialog = () => {
    showChatDialog.value = false;
    chatInput.value = '';
    chatResponse.value = '';
    sendDialogMask(false);
};

// Track message count before sending so we can detect new AI messages
let messageCountBeforeSend = 0;
let autoCloseTimer = null;

const sendChatMessage = () => {
    const text = chatInput.value.trim();
    if (!text) return;
    
    // Add user message to chatStore so web UI sees it too
    chatStore.addMessage({ text, sender: 'user' });
    
    console.log('📤 Desktop Pet sending:', text);
    chatInput.value = '';
    chatResponse.value = '⚡ Processing your message...';
    
    // Record current message count to detect new AI response
    messageCountBeforeSend = chatStore.messages.length;
    
    // Send through WebSocket service (same backend as web version)
    websocketService.sendMessage({ text });
    
    showToastMessage('Message sent!', 'success');
};

// Animation Loop
const animate = () => {
  animationFrameId = requestAnimationFrame(animate);
  const delta = clock.getDelta();
  
  updateMovement(delta); // Update position!
  sendPositionUpdate(); // Send position to backend
  
  if (vrmRef.value) vrmRef.value.update(delta);
  if (mixer) mixer.update(delta);
  
  renderer.render(scene, camera);
};

// Load Model
const loadVRMModel = () => {
  const loader = new GLTFLoader();
  loader.register((parser) => new VRMLoaderPlugin(parser));
  
  loader.load('/avatar.vrm', (gltf) => {
    const vrm = gltf.userData.vrm;
    if (!vrm) return;
    
    VRMUtils.removeUnnecessaryVertices(gltf.scene);
    VRMUtils.removeUnnecessaryJoints(gltf.scene);
    
    vrmRef.value = vrm;
    
    // Create wrapper for rotation/positioning
    const wrapper = new THREE.Group();
    characterWrapperGroup = wrapper;
    wrapper.add(vrm.scene);
    scene.add(wrapper);
    
    // Initial pose
    VRMUtils.rotateVRM0(vrm);
    
    // Relax arms immediately to avoid T-pose flash before animations load
    relaxArms(vrm);
    
    // Create invisible click bounding box for fast raycasting
    clickBoundingBox = createClickBoundingBox(vrm.scene);
    wrapper.add(clickBoundingBox);

    updateBounds(); // Set initial bounds and Y position
    
    // Start Decision Loop
    decideNextAction();
    
    // Create AnimationMixer
    mixer = new THREE.AnimationMixer(vrm.scene);
    
    // Load Animations
    loadIdleAnimation(); // Start with idle
    loadWalkingAnimation(); // Preload walk
    loadWavingAnimation(); // Preload wave
    loadTurnAnimations(); // Preload turns
    
    // Start animation loop
    animate();
    loadingModel.value = false;
  });
};

// Initialize the Three.js scene
const initScene = () => {
  scene = new THREE.Scene();
  
  // Create camera with transparent background settings
  // Camera position - optimized for full body view (moved back to make character smaller)
  camera = new THREE.PerspectiveCamera(
    30,
    window.innerWidth / window.innerHeight,
    0.1,
    20
  );
  
  renderer = new THREE.WebGLRenderer({ 
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true
  });
  
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setClearColor(0x000000, 0); // Fully transparent
  
  canvasContainer.value.appendChild(renderer.domElement);
  
  camera.position.set(0, 1.4, 10.5);
  camera.lookAt(new THREE.Vector3(0, 0.8, 0));
  
  // Lighting
  const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
  keyLight.position.set(1, 1, 2);
  scene.add(keyLight);
  
  const fillLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(fillLight);
  
  const backLight = new THREE.DirectionalLight(0xffffff, 0.5);
  backLight.position.set(-1, 1, -2);
  scene.add(backLight);

  clock = new THREE.Clock();
  
  loadVRMModel();
  
  // Connect to WebSocket server
  connectWebSocket();
  
  window.addEventListener('resize', onWindowResize);
  window.addEventListener('click', onCanvasClick);
};

// WebSocket connection with auto-reconnect
const connectWebSocket = () => {
    try {
        ws = new WebSocket('ws://localhost:8765');
        
        ws.onopen = () => {
            console.log('WebSocket connected to position server');
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting in 3s...');
            setTimeout(connectWebSocket, 3000);
        };
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
        setTimeout(connectWebSocket, 3000);
    }
};

// --- Voice Recognition Functions ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const initSpeechRecognition = () => {
  if (!SpeechRecognition) {
    showToastMessage('Voice input not supported in this browser', 'error');
    return false;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false; // Single utterance mode for desktop pet
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    console.log('🎤 Voice input started');
    isListening.value = true;
    hasError.value = false;
    showToastMessage('🎤 Listening...', 'info');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log('✅ Recognized:', transcript);
    
    // Send to AI via WebSocket
    sendMessageToAI(transcript);
    
    showToastMessage(`You said: "${transcript}"`, 'success');
  };

  recognition.onerror = (event) => {
    console.error('❌ Speech recognition error:', event.error);
    hasError.value = true;
    
    let errorMessage = 'Voice input error';
    switch(event.error) {
      case 'no-speech':
        errorMessage = 'No speech detected';
        break;
      case 'audio-capture':
        errorMessage = 'No microphone found';
        break;
      case 'not-allowed':
        errorMessage = 'Microphone access denied';
        break;
      default:
        errorMessage = `Error: ${event.error}`;
    }
    
    showToastMessage(errorMessage, 'error');
    isListening.value = false;
  };

  recognition.onend = () => {
    console.log('🎤 Voice recognition ended');
    isListening.value = false;
  };

  return true;
};

const toggleVoiceInput = () => {
  if (!recognition) {
    const initialized = initSpeechRecognition();
    if (!initialized) return;
  }

  if (isListening.value) {
    recognition.stop();
    isListening.value = false;
    showToastMessage('🎤 Voice input stopped', 'info');
  } else {
    hasError.value = false;
    try {
      recognition.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
      recognition = null;
      initSpeechRecognition();
      try {
        recognition.start();
      } catch (retryError) {
        showToastMessage('Failed to start voice input', 'error');
      }
    }
  }
};

const sendMessageToAI = (text) => {
  if (!text || !text.trim()) return;
  
  console.log('📤 Sending to AI:', text);
  
  // Send through WebSocket service (same as web version)
  websocketService.sendMessage({
    text: text.trim()
  });
  
  showToastMessage('🤖 AI is thinking...', 'info');
};

const showToastMessage = (message, type = 'info') => {
  toastMessage.value = message;
  toastType.value = type;
  showToast.value = true;
  
  setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

// Handle window resize
const onWindowResize = () => {
  if (!canvasContainer.value) return;
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  updateBounds();
};

onMounted(async () => {
  if (canvasContainer.value) {
    initScene();
    
    // Add transparent background class to body and remove any global background image
    document.body.style.backgroundColor = 'transparent';
    document.body.style.backgroundImage = 'none'; // REMOVE GRID
    document.documentElement.style.backgroundColor = 'transparent';
    document.documentElement.style.backgroundImage = 'none';
    
    const appInfo = document.getElementById('app');
    if (appInfo) {
        appInfo.style.backgroundColor = 'transparent';
        appInfo.style.backgroundImage = 'none';
        appInfo.style.boxShadow = 'none'; // Remove potential shadows
    }
  }
  
  
  // Connect chat WebSocket with the correct authenticated user ID
  // Priority: 1) URL parameter, 2) localStorage, 3) backend API
  
  // 1. Check URL parameter first (for QWebEngineView)
  const urlParams = new URLSearchParams(window.location.search);
  let userId = urlParams.get('userId');
  
  if (userId) {
    console.log(`🔗 Desktop Pet using user ID from URL parameter: ${userId}`);
  } else {
    // 2. Try localStorage (for regular browser)
    const userDataStr = localStorage.getItem('user');
    
    if (userDataStr) {
      try {
        const userData = JSON.parse(userDataStr);
        if (userData.sub) {
          userId = userData.sub;
          console.log(`🔐 Desktop Pet using authenticated user ID from localStorage: ${userId}`);
        }
      } catch (e) {
        console.warn('⚠️ Failed to parse user data from localStorage');
      }
    }
    
    // 3. Fallback to backend API
    if (!userId) {
      try {
        const resp = await fetch('http://localhost:8000/api/auth/current-user');
        const data = await resp.json();
        if (data.user_id) {
          userId = data.user_id;
          console.log(`🌐 Desktop Pet using user ID from backend API: ${userId}`);
        }
      } catch (e) {
        console.warn('⚠️ Failed to fetch user from backend API');
      }
    }
  }
  
  // Final fallback
  if (!userId) {
    userId = 'user_default';
    console.warn('⚠️ No user ID found, using default: user_default');
  }
  
  console.log(`🔑 Desktop Pet connecting as user: ${userId}`);
  websocketService.connect(userId);
  
  // Initialize conversationStore with the same user ID
  conversationStore.currentUserId = userId;
  
  // Watch AI status changes to show real-time status in desktop pet dialog
  watch(
    () => chatStore.aiStatusActive,
    (active) => {
      if (showChatDialog.value && active && chatStore.aiStatus) {
        chatResponse.value = `⚡ ${chatStore.aiStatus}`;
      }
    }
  );
  watch(
    () => chatStore.aiStatus,
    (status) => {
      if (showChatDialog.value && chatStore.aiStatusActive && status) {
        chatResponse.value = `⚡ ${status}`;
      }
    }
  );

  // Watch chatStore messages for AI responses to display in the dialog
  watch(
    () => chatStore.messages.length ? chatStore.messages[chatStore.messages.length - 1] : null,
    (lastMsg) => {
      if (!showChatDialog.value || !lastMsg || lastMsg.sender !== 'ai') return;
      
      // Update the dialog response text (works for both streaming & non-streaming)
      chatResponse.value = lastMsg.text || '';
      
      // Clear previous auto-close timer
      if (autoCloseTimer) clearTimeout(autoCloseTimer);
      
      // If the message is final (not streaming), auto-close after 10s
      if (!lastMsg.streaming) {
        autoCloseTimer = setTimeout(() => {
          if (showChatDialog.value) closeChatDialog();
        }, 10000);
      }
    },
    { deep: true }
  );
});

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  
  // Stop voice recognition
  if (recognition && isListening.value) {
    recognition.stop();
  }
  
  // Clear timers
  if (autoSendTimer) {
    clearTimeout(autoSendTimer);
  }
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer);
  }
  
  // Close position WebSocket connection
  if (ws) {
    ws.close();
    ws = null;
  }
  
  // Disconnect chat WebSocket
  websocketService.disconnect();
  
  window.removeEventListener('resize', onWindowResize);
  window.removeEventListener('click', onCanvasClick);
  // Restore background
  document.body.style.backgroundColor = '';
  document.body.style.backgroundImage = '';
  document.documentElement.style.backgroundColor = '';
  document.documentElement.style.backgroundImage = '';
});
</script>

<style>
/* Global overrides for this view */
body, html, #app {
  background-color: transparent !important;
  background-image: none !important;
  box-shadow: none !important;
}
</style>

<style scoped>
.desktop-pet-container {
  width: 100vw;
  height: 100vh;
  background: transparent !important;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: auto; /* Ensure clicks are captured */
  position: relative;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
}



@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.5);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 6px 25px rgba(245, 87, 108, 0.8);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* Toast Notification */
.toast {
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 2000;
  animation: slideDown 0.3s ease;
  backdrop-filter: blur(10px);
}

.toast.info {
  background: rgba(102, 126, 234, 0.95);
}

.toast.success {
  background: rgba(76, 209, 55, 0.95);
}

.toast.error {
  background: rgba(255, 107, 107, 0.95);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

/* Chat Dialog */
.chat-dialog {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  pointer-events: auto;
}

.chat-dialog-inner {
  background: rgba(15, 18, 30, 0.95);
  border: 1px solid rgba(0, 246, 255, 0.4);
  border-radius: 16px;
  padding: 12px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(0, 246, 255, 0.15),
    inset 0 0 30px rgba(0, 246, 255, 0.03);
  backdrop-filter: blur(16px);
  min-width: 420px;
  max-width: 550px;
}

.chat-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 246, 255, 0.2);
  border-radius: 10px;
  padding: 10px 14px;
  color: #E8EDFF;
  font-size: 14px;
  font-family: 'Rajdhani', sans-serif;
  outline: none;
  transition: all 0.2s ease;
}

.chat-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.chat-input:focus {
  border-color: rgba(0, 246, 255, 0.5);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 12px rgba(0, 246, 255, 0.15);
}

.chat-send-btn {
  padding: 8px 16px;
  border-radius: 10px;
  border: none;
  background: #00C8D6;
  color: #0a0e1a;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.chat-send-btn:hover:not(:disabled) {
  background: #00E5F0;
  box-shadow: 0 0 14px rgba(0, 246, 255, 0.4);
  transform: scale(1.05);
}

.chat-send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.chat-close-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 80, 80, 0.7);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.chat-close-btn:hover {
  background: rgba(255, 60, 60, 0.9);
  box-shadow: 0 0 10px rgba(255, 80, 80, 0.4);
}

.chat-response {
  margin-top: 10px;
  padding: 10px 14px;
  background: rgba(0, 246, 255, 0.05);
  border-left: 3px solid rgba(0, 246, 255, 0.4);
  border-radius: 0 8px 8px 0;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  line-height: 1.5;
  max-height: 120px;
  overflow-y: auto;
}

.response-label {
  color: #00F6FF;
  font-weight: 600;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 0.5px;
}

/* Slide transition */
.chat-slide-enter-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 1, 1);
}

.chat-slide-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.95);
}

.chat-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.95);
}
</style>
