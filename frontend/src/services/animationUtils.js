import * as THREE from 'three';

/**
 * Mixamo → VRM bone name mapping
 * Supports both mixamorig: prefix and J_Bip_ prefix
 */
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
  'J_Bip_L_ToeBase': 'leftToes',
  'J_Bip_R_UpperLeg': 'rightUpperLeg',
  'J_Bip_R_LowerLeg': 'rightLowerLeg',
  'J_Bip_R_Foot': 'rightFoot',
  'J_Bip_R_ToeBase': 'rightToes',
};

/**
 * Retarget an FBX AnimationClip to work with a VRM model.
 * Maps bone names from Mixamo/VRoid format to the VRM humanoid skeleton.
 * 
 * @param {THREE.AnimationClip} clip - The original FBX animation clip
 * @param {object} vrm - The VRM model instance
 * @param {object} options - Optional settings
 * @param {boolean} options.filterLegs - If true, remove leg/foot tracks
 * @returns {THREE.AnimationClip} The retargeted clip
 */
export function retargetClip(clip, vrm, options = {}) {
  if (!vrm || !vrm.humanoid) {
    console.warn('retargetClip: VRM humanoid not available, returning original clip');
    return clip;
  }

  const tracks = [];
  let mappedCount = 0;
  let skippedCount = 0;

  clip.tracks.forEach((track) => {
    const trackSplits = track.name.split('.');
    const boneName = trackSplits[0];
    const property = trackSplits[1];

    // Filter ALL position tracks (prevents root motion drift/teleport on loop)
    // Mixamo FBX hips position contains root motion that causes the character
    // to jump from one side to another when the animation loops.
    if (property === 'position') {
      return;
    }

    // Optionally filter leg tracks
    if (options.filterLegs) {
      const lower = boneName.toLowerCase();
      if (lower.includes('leg') || lower.includes('foot') || lower.includes('toe')
          || lower.includes('upleg') || lower.includes('upperleg') || lower.includes('lowerleg')) {
        return;
      }
    }

    let vrmBoneName = mixamoVRMMap[boneName];

    // Fallback: if boneName is already a valid VRM humanoid bone name
    if (!vrmBoneName && Object.values(mixamoVRMMap).includes(boneName)) {
      vrmBoneName = boneName;
    }

    if (vrmBoneName) {
      const vrmNode = vrm.humanoid.getNormalizedBoneNode(vrmBoneName);
      if (vrmNode) {
        const newTrackName = `${vrmNode.name}.${property}`;
        
        // For hips quaternion track, strip out Y-axis rotation to prevent
        // root motion turning. Mixamo idle animations slowly rotate the
        // character, causing a sudden snap when the animation loops.
        if (vrmBoneName === 'hips' && property === 'quaternion') {
          const values = new Float32Array(track.values.length);
          const q = new THREE.Quaternion();
          const euler = new THREE.Euler();
          for (let i = 0; i < track.values.length; i += 4) {
            q.set(track.values[i], track.values[i+1], track.values[i+2], track.values[i+3]);
            euler.setFromQuaternion(q, 'YXZ');
            euler.y = 0; // Zero out Y-axis rotation (turning)
            q.setFromEuler(euler);
            values[i]   = q.x;
            values[i+1] = q.y;
            values[i+2] = q.z;
            values[i+3] = q.w;
          }
          const newTrack = new track.constructor(newTrackName, track.times, values);
          tracks.push(newTrack);
          mappedCount++;
          console.log('🔧 Hips Y-rotation stripped to prevent root motion turning');
        } else {
          const newTrack = new track.constructor(newTrackName, track.times, track.values);
          tracks.push(newTrack);
          mappedCount++;
        }
      } else {
        skippedCount++;
      }
    } else {
      skippedCount++;
    }
  });

  console.log(`🎬 retargetClip: ${mappedCount} tracks mapped, ${skippedCount} skipped (from ${clip.tracks.length} total)`);
  
  return new THREE.AnimationClip(clip.name || 'retargetedClip', clip.duration, tracks);
}

/**
 * Relax arms from T-pose to a natural resting position.
 * Call this when no animation is playing to avoid T-pose.
 */
export function relaxArms(vrm) {
  if (!vrm || !vrm.humanoid) return;
  const leftArm = vrm.humanoid.getRawBoneNode('leftUpperArm');
  const rightArm = vrm.humanoid.getRawBoneNode('rightUpperArm');
  if (leftArm) leftArm.rotation.z = 1.2;
  if (rightArm) rightArm.rotation.z = -1.2;
}

/**
 * Create an invisible bounding box mesh for fast click detection.
 * Much faster than recursive raycasting against hundreds of VRM meshes.
 */
export function createClickBoundingBox(vrmScene) {
  const bbox = new THREE.Box3().setFromObject(vrmScene);
  const size = bbox.getSize(new THREE.Vector3());
  const center = bbox.getCenter(new THREE.Vector3());

  const geometry = new THREE.BoxGeometry(size.x, size.y, size.z);
  const material = new THREE.MeshBasicMaterial({ visible: false });
  const clickMesh = new THREE.Mesh(geometry, material);
  clickMesh.name = 'clickBoundingBox';

  // Position at the center of the VRM bounding box (in local space of parent)
  clickMesh.position.copy(center);

  return clickMesh;
}
