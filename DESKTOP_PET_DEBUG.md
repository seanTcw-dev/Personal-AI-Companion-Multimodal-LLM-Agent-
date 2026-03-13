# Desktop Pet — Debug & Fix Report

## Overview

The Desktop Pet is a PyQt6-based application that renders a VRM anime character as a transparent, always-on-top overlay on the desktop. The character walks around, idles, and responds to clicks with a waving animation. It uses:

- **PyQt6 + QWebEngineView** — Transparent frameless window covering the full screen
- **Three.js + @pixiv/three-vrm** — 3D rendering of VRM model inside a Vite frontend (`/desktop-pet` route)
- **WebSocket** — Sends character screen position from frontend to PyQt6 backend to update the window mask (clickable region)
- **FBX Animations (Mixamo)** — Idle, Walk, Wave, Turn Left/Right, Hit

The same VRM model is also rendered in the main web chat interface (`CharacterView.vue`), which shares many of the same issues.

---

## Issues Encountered & Solutions

### 1. Click Lag — Recursive Raycasting on Complex Model

**Symptom:** Clicking on the 3D model caused noticeable frame drops and stuttering.

**Root Cause:** The click handler used `raycaster.intersectObjects(vrmRef.value.scene.children, true)` with `recursive=true`. A VRM model contains hundreds of child meshes (hair strands, clothing pieces, skin segments, bones). Testing ray intersection against all of them every click is an expensive O(n) operation that blocks the main thread.

**Fix:** Created an invisible `THREE.BoxGeometry` bounding box (`createClickBoundingBox()`) that wraps the character. Click detection now tests against a single simple cube instead of hundreds of meshes.

```js
// Before (slow)
raycaster.intersectObjects(vrmRef.value.scene.children, true);

// After (fast)
raycaster.intersectObject(clickBoundingBox);
```

**File:** `frontend/src/views/DesktopPetView.vue`, `frontend/src/services/animationUtils.js`

---

### 2. Wave Animation Sometimes Not Triggering

**Symptom:** Clicking the character sometimes did nothing — no wave animation played.

**Root Cause:** Missing `return` statement in `triggerWaveInteraction()`. When the character was already facing the camera (`diff < 0.1`), it called `playWaveAnimation()` but did **not** return. The code fell through to the turn animation logic below, which conflicted with the wave that was just started.

```js
// Bug
if (Math.abs(diff) < 0.1) {
    characterWrapperGroup.rotation.y = 0;
    playWaveAnimation();
    // ← No return! Falls through to turn logic, conflicting with wave
}
```

**Fix:** Added `return` after the early wave call.

**File:** `frontend/src/views/DesktopPetView.vue`

---

### 3. T-Pose — Animations Not Applying to VRM Model

**Symptom:** The character remained in T-pose (arms straight out) instead of playing animations. Sometimes animations partially worked but the pose looked broken.

**Root Cause:** FBX animations exported from Mixamo use bone names like `mixamorig:Hips`, `mixamorig:LeftArm`, etc. The VRM model uses completely different bone names: `J_Bip_C_Hips`, `J_Bip_L_UpperArm`, etc.

Three.js `AnimationMixer` matches animation tracks to bones by **name**. When the names don't match, zero tracks are applied, and the model silently stays in its rest pose (T-pose). No error is thrown.

The project already had a complete bone mapping (`mixamoVRMMap`) and `retargetClip()` function in `ModelSettings.vue`, but neither `CharacterView.vue` nor `DesktopPetView.vue` used it. They loaded FBX clips and passed them directly to the mixer.

**Fix:**
1. Extracted `retargetClip()` and bone mapping into a shared module: `frontend/src/services/animationUtils.js`
2. All animation loading in both views now passes through `retargetClip()` to remap bone names
3. Added `relaxArms()` immediately after VRM model load to rotate upper arms away from T-pose before animations finish loading (prevents visual flash)

```js
// Before (T-pose)
idleAction.value = mixer.clipAction(fbx.animations[0]);

// After (works)
const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value);
idleAction.value = mixer.clipAction(retargetedClip);
```

**Files:** `frontend/src/services/animationUtils.js` (new), `frontend/src/views/DesktopPetView.vue`, `frontend/src/components/character/CharacterView.vue`

---

### 4. Turn Animation Looked Instant / "Snapping"

**Symptom:** When clicking the character while it was walking sideways, it appeared to instantly snap to face the camera instead of smoothly turning.

**Root Cause:** The turn animation only drove bone rotations (body turning), but the `characterWrapperGroup` (the THREE.Group containing the entire character) stayed at its walking rotation (`PI/2` or `-PI/2`) throughout the animation. When the turn finished, the wrapper's `rotation.y` was instantly set to `0`, causing a visual snap.

**Fix:** Added a synchronized `requestAnimationFrame` loop that smoothly interpolates `characterWrapperGroup.rotation.y` from its current value to `0` over the duration of the turn animation, using an ease-in-out curve. Also slowed down the turn animation (`timeScale = 0.8`) for a more natural feel.

**File:** `frontend/src/views/DesktopPetView.vue`

---

### 5. Wave Animation Freezing / Getting Stuck

**Symptom:** After waving, the character would freeze in the last frame of the wave animation and never return to idle or walking.

**Root Cause:** Two issues combined:
1. Wave was set to `LoopOnce` + `clampWhenFinished = true`, which freezes on the last frame after the clip ends
2. The backup timeout's condition `characterWrapperGroup.rotation.y !== 0` was no longer true (the smooth rotation had already set it to 0), so the fallback never triggered
3. The mixer's `finished` event may not fire reliably after retargeting

**Fix:**
1. Changed wave to `LoopRepeat` with an 8-second `setTimeout` to control duration
2. Replaced the conditional backup timeout with an unconditional one
3. Added `turnHandled` flag to prevent `finishTurn()` from being called twice (by both `finished` event and backup timeout)
4. After wave ends, character idles for 10 seconds before `decideNextAction()`

**File:** `frontend/src/views/DesktopPetView.vue`

---

### 6. Turn Direction Was Inverted

**Symptom:** When the character was walking right and clicked, it played the Right Turn animation (turning further right) instead of Left Turn (turning back to face camera).

**Root Cause:** The turn direction logic was inverted. Walking right means `rotation.y = PI/2`, and the `diff` to reach `0` is negative. The code mapped `diff > 0` to Left Turn, but it should be the opposite.

**Fix:** Swapped the condition: `const isLeftTurn = diff < 0;`

**File:** `frontend/src/views/DesktopPetView.vue`

---

### 7. Legs Not Frozen in Web Chat View

**Symptom:** In the web chat interface (`CharacterView.vue`), the character's legs moved during idle and wave animations. The original code had leg freezing but it was removed during the fix process.

**Root Cause:** The original `freezeLegs()` function overwrote bone transforms **every frame** after `mixer.update()`, which fought with the animation mixer and caused visual stutter. It was removed, but the replacement (`filterLegs` option in `retargetClip`) was initially only applied to wave/walk/hit animations, not to the idle animation.

**Fix:** Added `filterLegs: true` to ALL animation loads in `CharacterView.vue` (idle, wave, walk, hit). This cleanly removes leg tracks at the clip level instead of fighting the mixer every frame. Also kept idle running during wave so the upper body is driven by wave while legs remain in rest pose.

```js
// Before (fights mixer every frame)
const freezeLegs = () => {
  Object.keys(legBones.value).forEach(key => {
    bone.position.copy(original.position);
    bone.rotation.copy(original.rotation);
  });
};
// Called in animate(): mixer.update(delta); freezeLegs();

// After (clean, at clip level)
const retargetedClip = retargetClip(fbx.animations[0], vrmRef.value, { filterLegs: true });
```

**File:** `frontend/src/components/character/CharacterView.vue`

---

## Key Takeaways

| Lesson | Detail |
|--------|--------|
| **Bone name retargeting is mandatory for VRM + Mixamo** | Without it, animations silently fail with no errors — the model just stays in T-pose |
| **Don't fight the AnimationMixer** | Overwriting bone transforms every frame after `mixer.update()` causes stutter. Filter unwanted tracks at the clip level instead |
| **Always add `return` after early exits** | A missing `return` caused code to fall through and trigger conflicting animation logic |
| **Reuse existing working code** | `ModelSettings.vue` already had perfect retargeting code — it just wasn't shared with the other views |
| **Use simplified geometry for raycasting** | Recursive raycasting against complex models (hundreds of meshes) is a performance killer. Use a bounding box instead |
| **Sync wrapper rotation with bone animation** | Turn animations drive bones, but if the parent Group isn't rotated in sync, the visual result is a sudden snap |
| **Use guards for async callbacks** | `turnHandled` flag prevents double execution when both `finished` event and backup timeout fire |

## Files Modified

| File | Changes |
|------|---------|
| `frontend/src/services/animationUtils.js` | **NEW** — Shared `retargetClip()`, `relaxArms()`, `createClickBoundingBox()` |
| `frontend/src/views/DesktopPetView.vue` | Retarget all animations, bounding box click, fix wave trigger, fix turn sync, fix wave freeze |
| `frontend/src/components/character/CharacterView.vue` | Retarget all animations, filter legs at clip level, remove `freezeLegs()`, add `relaxArms()` |
