<template>
  <div class="settings-container">
    <!-- Left Panel: Controls -->
    <div class="controls-panel">
      <div class="panel-header">
        <h1 class="page-title">3D STUDIO</h1>
        <p class="page-subtitle">Character & Animation Preview</p>
      </div>

      <div class="settings-group">
        <h2 class="group-title">👤 Character Model</h2>
        
        <div class="control-item">
          <label>Select Character</label>
          <select v-model="selectedCharacter" @change="handleCharacterChange" class="input-field">
            <option value="default">Default (Suzune)</option>
            <option value="custom">Custom Upload</option>
          </select>
        </div>

        <div class="control-item upload-box">
          <label>Upload VRM File</label>
          <input type="file" ref="vrmInput" accept=".vrm" @change="handleVRMUpload" hidden />
          <button class="btn-upload" @click="$refs.vrmInput.click()">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            {{ vrmFileName || 'Choose .vrm file' }}
          </button>
        </div>
      </div>

      <div class="settings-group">
        <h2 class="group-title">🎬 Animation</h2>
        
        <div class="control-item">
          <label>Select Animation</label>
          <select v-model="selectedAnimation" @change="handleAnimationChange" class="input-field">
            <option value="none">T-Pose / Idle</option>
            <option value="wave">Waving (Default)</option>
            <option value="custom">Custom Upload (.fbx)</option>
          </select>
        </div>

        <div class="control-item upload-box">
          <label>Upload FBX Animation</label>
          <input type="file" ref="fbxInput" accept=".fbx" @change="handleFBXUpload" hidden />
          <button class="btn-upload" @click="$refs.fbxInput.click()">
             <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            {{ fbxFileName || 'Choose .fbx file' }}
          </button>
        </div>

        <div class="control-item">
          <label>Animation Speed: {{ animationSpeed }}x</label>
          <input type="range" v-model="animationSpeed" min="0.1" max="2.0" step="0.1" class="slider" @input="updateSpeed">
        </div>

        <div class="control-actions">
           <button class="btn-primary" @click="toggleAnimation">
            {{ isPaused ? '▶ Play' : '⏸ Pause' }}
           </button>
           <button class="btn-secondary" @click="resetAnimation">
            ↺ Restart
           </button>
        </div>
      </div>

      <div class="bottom-actions">
        <button class="btn-back" @click="goBack">
           <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
           Back to Chat
        </button>
      </div>
    </div>

    <!-- Right Panel: 3D Preview -->
    <div class="preview-panel" ref="canvasContainer">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">{{ loadingStatus }}</div>
      </div>
      <!-- Canvas will be appended here -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const router = useRouter();
const canvasContainer = ref(null);
const isLoading = ref(true);
const loadingStatus = ref('Initializing 3D Engine...');
const vrmFileName = ref('');
const fbxFileName = ref('');

// State
const selectedCharacter = ref('default');
const selectedAnimation = ref('wave');
const animationSpeed = ref(1.0);
const isPaused = ref(false);

// Three.js variables
let scene, camera, renderer, clock, controls;
let vrm = null;
let mixer = null;
let currentAction = null;
let animationReqId = null;

// Built-in assets paths (These should exist in public folder as per project structure)
const DEFAULT_VRM_PATH = '/avatar.vrm'; 
const DEFAULT_ANIM_PATH = '/animations/AvatarSample_A@Waving.fbx';

onMounted(() => {
  initScene();
});

onBeforeUnmount(() => {
  if (animationReqId) cancelAnimationFrame(animationReqId);
  if (renderer) renderer.dispose();
  if (mixer) mixer.stopAllAction();
  window.removeEventListener('resize', onWindowResize);
});

const goBack = () => {
  router.push('/chat');
};

const initScene = async () => {
  // Setup Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0E101B);
  
  // Grid Helper
  const gridHelper = new THREE.GridHelper(10, 10, 0x00F6FF, 0x222222);
  scene.add(gridHelper);

  // Setup Camera
  const width = canvasContainer.value.clientWidth;
  const height = canvasContainer.value.clientHeight;
  camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 20);
  camera.position.set(0, 1.5, 4.0);

  // Setup Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  canvasContainer.value.appendChild(renderer.domElement);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1.0, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // Lighting (Brightened)
  const keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
  keyLight.position.set(1, 1.5, 2);
  scene.add(keyLight);
  
  const fillLight = new THREE.AmbientLight(0xffffff, 1.2);
  scene.add(fillLight);
  
  const rimLight = new THREE.DirectionalLight(0x00F6FF, 1.5);
  rimLight.position.set(-0.5, 1.5, -1.5);
  scene.add(rimLight);

  // Extra front light for face (Subtle fill)
  const frontLight = new THREE.DirectionalLight(0xffffff, 0.3);
  frontLight.position.set(0, 0, 2);
  scene.add(frontLight);

  clock = new THREE.Clock();
  
  window.addEventListener('resize', onWindowResize);

  // Initial Load
  await loadVRM(DEFAULT_VRM_PATH);
  
  // Start Loop
  animate();
};

const loadVRM = (url) => {
  return new Promise((resolve, reject) => {
    isLoading.value = true;
    loadingStatus.value = 'Loading VRM Model...';
    
    if (vrm) {
      scene.remove(vrm.scene);
      VRMUtils.deepDispose(vrm.scene);
      vrm = null;
    }

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(url, (gltf) => {
      vrm = gltf.userData.vrm;
      
      // Cleanup vertices (Crucial for retargeting!)
      VRMUtils.removeUnnecessaryVertices(gltf.scene);

      // Rotate VRM to face camera
      VRMUtils.rotateVRM0(vrm);
      
      // Ensure all parts are rendered
      vrm.scene.traverse((obj) => {
        obj.frustumCulled = false;
      });
      
      scene.add(vrm.scene);
      
      // Mixer
      mixer = new THREE.AnimationMixer(vrm.scene);
      
      // Debug: Check humanoid bones
      if (vrm.humanoid) {
        console.log('✅ VRM Humanoid found');
        console.log('📊 Humanoid bones:', Object.keys(vrm.humanoid.humanBones || {}).length);
        console.log('📊 Raw bones:', Object.keys(vrm.humanoid.rawHumanBones || {}).length);
      } else {
        console.warn('⚠️ VRM has no humanoid!');
      }
      
      // Fix T-pose arms if no animation
      if (vrm.humanoid) {
         relaxArms(vrm);
      }
      
      isLoading.value = false;
      console.log('✅ VRM Loaded');

      // If we have a selected animation, load it with a slight delay to ensure readiness
      if (selectedAnimation.value === 'wave') {
        setTimeout(() => {
             loadFBX(DEFAULT_ANIM_PATH);
        }, 500);
      }

      resolve(vrm);
    }, 
    (progress) => {
       loadingStatus.value = `Loading VRM: ${Math.round((progress.loaded / progress.total) * 100)}%`;
    },
    (error) => {
       console.error(error);
       isLoading.value = false;
       alert('Failed to load VRM');
       reject(error);
    });
  });
};

// Load Mixamo Animation - Direct Application (matching test-vrm-animation.html)
// 🗺️ Mixamo to VRM Bone Mapping
// 🗺️ Bone Mapping: Mixamo + VRM/VRoid Standard Names
const mixamoVRMMap = {
  // Mixamo format
  'mixamorig:Hips': 'hips',
  'mixamorig:Spine': 'spine',
  'mixamorig:Spine1': 'chest',
  'mixamorig:Spine2': 'upperChest',
  'mixamorig:Neck': 'neck',
  'mixamorig:Head': 'head',
  'mixamorig:LeftShoulder': 'leftShoulder',
  'mixamorig:LeftArm': 'leftUpperArm',
  'mixamorig:LeftForeArm': 'leftLowerArm',
  'mixamorig:LeftHand': 'leftHand',
  'mixamorig:LeftHandThumb1': 'leftThumbMetacarpal',
  'mixamorig:LeftHandThumb2': 'leftThumbProximal',
  'mixamorig:LeftHandThumb3': 'leftThumbDistal',
  'mixamorig:LeftHandIndex1': 'leftIndexProximal',
  'mixamorig:LeftHandIndex2': 'leftIndexIntermediate',
  'mixamorig:LeftHandIndex3': 'leftIndexDistal',
  'mixamorig:LeftHandMiddle1': 'leftMiddleProximal',
  'mixamorig:LeftHandMiddle2': 'leftMiddleIntermediate',
  'mixamorig:LeftHandMiddle3': 'leftMiddleDistal',
  'mixamorig:LeftHandRing1': 'leftRingProximal',
  'mixamorig:LeftHandRing2': 'leftRingIntermediate',
  'mixamorig:LeftHandRing3': 'leftRingDistal',
  'mixamorig:LeftHandPinky1': 'leftLittleProximal',
  'mixamorig:LeftHandPinky2': 'leftLittleIntermediate',
  'mixamorig:LeftHandPinky3': 'leftLittleDistal',
  'mixamorig:RightShoulder': 'rightShoulder',
  'mixamorig:RightArm': 'rightUpperArm',
  'mixamorig:RightForeArm': 'rightLowerArm',
  'mixamorig:RightHand': 'rightHand',
  'mixamorig:RightHandThumb1': 'rightThumbMetacarpal',
  'mixamorig:RightHandThumb2': 'rightThumbProximal',
  'mixamorig:RightHandThumb3': 'rightThumbDistal',
  'mixamorig:RightHandIndex1': 'rightIndexProximal',
  'mixamorig:RightHandIndex2': 'rightIndexIntermediate',
  'mixamorig:RightHandIndex3': 'rightIndexDistal',
  'mixamorig:RightHandMiddle1': 'rightMiddleProximal',
  'mixamorig:RightHandMiddle2': 'rightMiddleIntermediate',
  'mixamorig:RightHandMiddle3': 'rightMiddleDistal',
  'mixamorig:RightHandRing1': 'rightRingProximal',
  'mixamorig:RightHandRing2': 'rightRingIntermediate',
  'mixamorig:RightHandRing3': 'rightRingDistal',
  'mixamorig:RightHandPinky1': 'rightLittleProximal',
  'mixamorig:RightHandPinky2': 'rightLittleIntermediate',
  'mixamorig:RightHandPinky3': 'rightLittleDistal',
  'mixamorig:LeftUpLeg': 'leftUpperLeg',
  'mixamorig:LeftLeg': 'leftLowerLeg',
  'mixamorig:LeftFoot': 'leftFoot',
  'mixamorig:LeftToeBase': 'leftToes',
  'mixamorig:RightUpLeg': 'rightUpperLeg',
  'mixamorig:RightLeg': 'rightLowerLeg',
  'mixamorig:RightFoot': 'rightFoot',
  'mixamorig:RightToeBase': 'rightToes',

  // VRM/VRoid Standard Format (J_Bip_...)
  'J_Bip_C_Hips': 'hips',
  'J_Bip_C_Spine': 'spine',
  'J_Bip_C_Chest': 'chest',
  'J_Bip_C_UpperChest': 'upperChest',
  'J_Bip_C_Neck': 'neck',
  'J_Bip_C_Head': 'head',
  'J_Bip_L_Shoulder': 'leftShoulder',
  'J_Bip_L_UpperArm': 'leftUpperArm',
  'J_Bip_L_LowerArm': 'leftLowerArm',
  'J_Bip_L_Hand': 'leftHand',
  'J_Bip_L_Thumb1': 'leftThumbMetacarpal',
  'J_Bip_L_Thumb2': 'leftThumbProximal',
  'J_Bip_L_Thumb3': 'leftThumbDistal',
  'J_Bip_L_Index1': 'leftIndexProximal',
  'J_Bip_L_Index2': 'leftIndexIntermediate',
  'J_Bip_L_Index3': 'leftIndexDistal',
  'J_Bip_L_Middle1': 'leftMiddleProximal',
  'J_Bip_L_Middle2': 'leftMiddleIntermediate',
  'J_Bip_L_Middle3': 'leftMiddleDistal',
  'J_Bip_L_Ring1': 'leftRingProximal',
  'J_Bip_L_Ring2': 'leftRingIntermediate',
  'J_Bip_L_Ring3': 'leftRingDistal',
  'J_Bip_L_Little1': 'leftLittleProximal',
  'J_Bip_L_Little2': 'leftLittleIntermediate',
  'J_Bip_L_Little3': 'leftLittleDistal',
  'J_Bip_R_Shoulder': 'rightShoulder',
  'J_Bip_R_UpperArm': 'rightUpperArm',
  'J_Bip_R_LowerArm': 'rightLowerArm',
  'J_Bip_R_Hand': 'rightHand',
  'J_Bip_R_Thumb1': 'rightThumbMetacarpal',
  'J_Bip_R_Thumb2': 'rightThumbProximal',
  'J_Bip_R_Thumb3': 'rightThumbDistal',
  'J_Bip_R_Index1': 'rightIndexProximal',
  'J_Bip_R_Index2': 'rightIndexIntermediate',
  'J_Bip_R_Index3': 'rightIndexDistal',
  'J_Bip_R_Middle1': 'rightMiddleProximal',
  'J_Bip_R_Middle2': 'rightMiddleIntermediate',
  'J_Bip_R_Middle3': 'rightMiddleDistal',
  'J_Bip_R_Ring1': 'rightRingProximal',
  'J_Bip_R_Ring2': 'rightRingIntermediate',
  'J_Bip_R_Ring3': 'rightRingDistal',
  'J_Bip_R_Little1': 'rightLittleProximal',
  'J_Bip_R_Little2': 'rightLittleIntermediate',
  'J_Bip_R_Little3': 'rightLittleDistal',
  'J_Bip_L_UpperLeg': 'leftUpperLeg',
  'J_Bip_L_LowerLeg': 'leftLowerLeg',
  'J_Bip_L_Foot': 'leftFoot',
  'J_Bip_L_ToeBase': 'leftToes', // Not always present
  'J_Bip_R_UpperLeg': 'rightUpperLeg',
  'J_Bip_R_LowerLeg': 'rightLowerLeg',
  'J_Bip_R_Foot': 'rightFoot',
  'J_Bip_R_ToeBase': 'rightToes', // Not always present

  // Root - REMOVE these to prevent conflicts with J_Bip_C_Hips
  // 'Root': 'hips', 
  // 'AvatarSample_A': 'hips' 
};

const retargetClip = (clip) => {
  const tracks = [];

  console.log(`🔍 Retargeting Clip: ${clip.name}, Total Tracks: ${clip.tracks.length}`);

  clip.tracks.forEach((track) => {
    // track.name format: "BoneName.position"
    const trackSplits = track.name.split('.');
    const boneName = trackSplits[0];
    const property = trackSplits[1];

    // 1. Filter out Position tracks for everything except Hips
    // This prevents the "exploding character" effect where limbs detach
    if (property === 'position' && mixamoVRMMap[boneName] !== 'hips') {
      return; 
    }

    let vrmBoneName = mixamoVRMMap[boneName];

    // Fallback: Check if boneName is ALREADY a valid VRM bone name (lowercase)
    if (!vrmBoneName && Object.values(mixamoVRMMap).includes(boneName)) {
        vrmBoneName = boneName;
    }

    if (vrmBoneName) {
      const vrmNode = vrm.humanoid.getNormalizedBoneNode(vrmBoneName);
      
      if (vrmNode) {
        const newTrackName = `${vrmNode.name}.${property}`;
        
        // 2. Scale Hips Position (Optional, but often needed if units differ cm vs m)
        // If the character jumps too high or sinks, we might need to scale the values here.
        // For now, let's keep it 1:1 but keep this comment in mind.
        
        console.log(`✅ Mapped: ${boneName} -> ${vrmNode.name} (${property})`);
        const newTrack = new track.constructor(newTrackName, track.times, track.values);
        tracks.push(newTrack);
      }
    }
  });

  return new THREE.AnimationClip('vrmAnimation', clip.duration, tracks);
};

const loadFBX = (fbxPath) => {
  if (!vrm || !mixer) {
    console.warn('❌ VRM not loaded yet!');
    return;
  }

  isLoading.value = true;
  loadingStatus.value = 'Loading animation...';

  const fbxLoader = new FBXLoader();

  fbxLoader.load(
    fbxPath,
    (fbx) => {
      console.log(`✅ FBX loaded: ${fbxPath}`);

      if (!fbx.animations || fbx.animations.length === 0) {
        console.warn('❌ No animations in FBX!');
        isLoading.value = false;
        return;
      }

      const fbxClip = fbx.animations[0];
      
      // 🎯 Manual Retargeting
      try {
        const vrmClip = retargetClip(fbxClip);
        console.log(`✅ Retargeted clip created: ${vrmClip.tracks.length} tracks`);

        if (currentAction) currentAction.stop();

        currentAction = mixer.clipAction(vrmClip);
        currentAction.setLoop(THREE.LoopRepeat);
        currentAction.timeScale = animationSpeed.value;
        currentAction.play();

        isLoading.value = false;
        isPaused.value = false;
        console.log(`▶️ Animation playing!`);
        
      } catch (error) {
        console.error(`❌ Retarget failed:`, error);
        alert(`Failed to retarget animation: ${error.message}`);
        isLoading.value = false;
      }
    },
    (progress) => {
       // Optional: progress
    },
    (error) => {
      console.error(`❌ FBX load error:`, error);
      isLoading.value = false;
    }
  );
};

const relaxArms = (vrmModel) => {
    const leftArm = vrmModel.humanoid.getRawBoneNode('leftUpperArm');
    const rightArm = vrmModel.humanoid.getRawBoneNode('rightUpperArm');
    if (leftArm) leftArm.rotation.z = 1.2;
    if (rightArm) rightArm.rotation.z = -1.2;
};

// Handlers
const handleCharacterChange = () => {
   if (selectedCharacter.value === 'default') {
       loadVRM(DEFAULT_VRM_PATH);
       vrmFileName.value = '';
   } else if (selectedCharacter.value === 'custom') {
       // Wait for file upload
       // $refs.vrmInput.click(); // Optional auto-trigger
   }
};

const handleVRMUpload = (event) => {
   const file = event.target.files[0];
   if (!file) return;
   
   vrmFileName.value = file.name;
   selectedCharacter.value = 'custom';
   const url = URL.createObjectURL(file);
   loadVRM(url);
};

const handleAnimationChange = () => {
   if (selectedAnimation.value === 'wave') {
       loadFBX(DEFAULT_ANIM_PATH);
   } else if (selectedAnimation.value === 'none') {
       if (currentAction) currentAction.stop();
   } else if (selectedAnimation.value === 'custom') {
       // Wait for upload
   }
};

const handleFBXUpload = (event) => {
   const file = event.target.files[0];
   if (!file) return;
   
   fbxFileName.value = file.name;
   selectedAnimation.value = 'custom';
   const url = URL.createObjectURL(file);
   loadFBX(url);
};

const updateSpeed = () => {
    if (currentAction) {
        currentAction.timeScale = animationSpeed.value;
    }
};

const toggleAnimation = () => {
    if (!currentAction) return;
    isPaused.value = !isPaused.value;
    currentAction.paused = isPaused.value;
};

const resetAnimation = () => {
    if (currentAction) {
        currentAction.reset();
        currentAction.play();
        isPaused.value = false;
    }
};

const onWindowResize = () => {
   if (!canvasContainer.value || !camera || !renderer) return;
   const width = canvasContainer.value.clientWidth;
   const height = canvasContainer.value.clientHeight;
   
   camera.aspect = width / height;
   camera.updateProjectionMatrix();
   renderer.setSize(width, height);
};

const animate = () => {
   animationReqId = requestAnimationFrame(animate);
   
   const delta = clock.getDelta();
   if (mixer) mixer.update(delta);
   if (vrm) vrm.update(delta);
   if (controls) controls.update();
   
   renderer.render(scene, camera);
};

</script>

<style scoped>
.settings-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #0E101B;
  color: white;
  overflow: hidden; /* Hide scrollbar */
}

/* Hide scrollbar for WebKit browsers */
::-webkit-scrollbar {
    display: none;
}

/* Left Panel */
.controls-panel {
  width: 350px;
  background: #0E101B;
  border-right: 1px solid #1a1f35;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
  z-index: 10;
  box-shadow: 2px 0 10px rgba(0,0,0,0.5);
}

.panel-header {
  margin-bottom: 30px;
  text-align: center;
  border-bottom: 1px solid rgba(0, 246, 255, 0.2);
  padding-bottom: 15px;
}

.page-title {
  font-family: 'Orbitron', sans-serif;
  color: #00F6FF;
  font-size: 24px;
  letter-spacing: 2px;
  margin: 0;
}

.page-subtitle {
  color: #667;
  font-size: 12px;
  margin: 5px 0 0 0;
}

/* Settings Groups */
.settings-group {
  margin-bottom: 30px;
}

.group-title {
  color: #00F6FF;
  font-size: 16px;
  text-transform: uppercase;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-item {
  margin-bottom: 15px;
}

.control-item label {
  display: block;
  font-size: 13px;
  color: #889;
  margin-bottom: 8px;
}

.input-field {
  width: 100%;
  background: #151929;
  border: 1px solid #2a3149;
  color: #fff;
  padding: 10px;
  border-radius: 6px;
  outline: none;
  font-family: 'Rajdhani', sans-serif;
}

.input-field:focus {
  border-color: #00F6FF;
}

.upload-box {
  margin-top: 10px;
}

.btn-upload {
  width: 100%;
  background: rgba(0, 246, 255, 0.1);
  border: 1px dashed rgba(0, 246, 255, 0.4);
  color: #00F6FF;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-upload:hover {
  background: rgba(0, 246, 255, 0.2);
}

.slider {
  width: 100%;
  height: 4px;
  background: #2a3149;
  border-radius: 2px;
  appearance: none;
  outline: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: #00F6FF;
  border-radius: 50%;
  cursor: pointer;
}

/* Actions */
.control-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.btn-primary, .btn-secondary {
  flex: 1;
  padding: 10px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  font-family: 'Rajdhani', sans-serif;
}

.btn-primary {
  background: #00F6FF;
  color: #000;
}

.btn-secondary {
  background: #2a3149;
  color: #fff;
}

.bottom-actions {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #1a1f35;
}

.btn-back {
  width: 100%;
  background: transparent;
  border: 1px solid #333;
  color: #888;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: 0.2s;
}

.btn-back:hover {
  border-color: #555;
  color: #fff;
}

/* Right Panel */
.preview-panel {
  flex: 1;
  position: relative;
  background: radial-gradient(circle at center, #1a1f35 0%, #0E101B 100%);
}

.loading-overlay {
  position: absolute;
  top: 0; 
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 246, 255, 0.3);
  border-top-color: #00F6FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-text {
  color: #00F6FF;
  font-size: 14px;
  letter-spacing: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
