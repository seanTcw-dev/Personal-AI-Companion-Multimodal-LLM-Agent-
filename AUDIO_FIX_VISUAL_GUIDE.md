# 🎭 Audio Detection Flow - Visual Guide

## The Problem (Before Fix)

```
┌─────────────────────────────────────────────────────────────────┐
│                     ❌ INFINITE LOOP BUG                         │
└─────────────────────────────────────────────────────────────────┘

    User                  Microphone              AI System
     👤                      🎤                      🤖
      │                       │                       │
      │   "Haha!"            │                       │
      ├──────────────────────>│                       │
      │                       │                       │
      │                       │  Detected: Happy      │
      │                       ├──────────────────────>│
      │                       │                       │
      │                       │                       │  AI: "What's 
      │                       │<──────────────────────┤  so funny?"
      │                       │    🔊 Audio plays     │
      │                       │                       │
      │                       │  ❌ PROBLEM:          │
      │                       │  Hears AI voice!      │
      │                       ├──────────────────────>│
      │                       │  Detected: Happy      │  
      │                       │  (from AI words)      │
      │                       │                       │
      │                       │<──────────────────────┤  AI responds
      │                       │    🔊 Audio plays     │  again!
      │                       │                       │
      │                       │  ❌ Hears again!      │
      │                       ├──────────────────────>│
      │                       │                       │
      │                       │                   💥 LOOP FOREVER!
```

---

## The Solution (After Fix)

```
┌─────────────────────────────────────────────────────────────────┐
│              ✅ PROTECTED WITH 3-LAYER DEFENSE                   │
└─────────────────────────────────────────────────────────────────┘

    User                  Microphone              AI System
     👤                      🎤                      🤖
      │                       │                       │
      │   "Haha!"            │                       │
      ├──────────────────────>│                       │
      │                       │                       │
      │                       │ ✅ Layer 1: Check    │
      │                       │ AI speaking? NO      │
      │                       │                       │
      │                       │ ✅ Layer 2: Check    │
      │                       │ Cooldown? NO         │
      │                       │                       │
      │                       │ ✅ Layer 3: Check    │
      │                       │ Duplicate? NO        │
      │                       │                       │
      │                       │  Detected: Happy ✅   │
      │                       ├──────────────────────>│
      │                       │                       │
      │                       │  [Cooldown: 5s] ⏳    │
      │                       │                       │
      │                       │◄──────────────────────┤  AI: "What's
      │                       │  🔊 AI SPEAKING ON    │  so funny?"
      │                       │                       │
      │                       │  🛡️ LAYER 1 ACTIVE   │
      │                       │  Ignoring all input   │
      │   Can't trigger!     │                       │
      ├──────────────────────>│  ❌ Blocked by L1    │
      │   (even if you try)  │                       │
      │                       │                       │
      │                       │  ✅ AI voice heard   │
      │                       │  but BLOCKED ✅       │
      │                       │                       │
      │                       │◄──────────────────────┤  Audio ends
      │                       │  🔊 AI SPEAKING OFF   │
      │                       │                       │
      │                       │  Still in cooldown... │
      │                       │  ⏳ 3 seconds left    │
      │                       │                       │
      │   Try again now      │                       │
      ├──────────────────────>│  ❌ Blocked by L2    │
      │   "Wow!"             │  (Cooldown active)    │
      │                       │                       │
      │    [Wait 5s total]   │                       │
      │                       │                       │
      │   After cooldown     │  ✅ All checks pass   │
      ├──────────────────────>│  Detected: Surprised  │
      │   "Amazing!"         ├──────────────────────>│  New response!
      │                       │                       │
```

---

## 3-Layer Defense System

```
┌─────────────────────────────────────────────────────────────────┐
│                    🛡️ PROTECTION LAYERS                         │
└─────────────────────────────────────────────────────────────────┘

                        Incoming Audio
                              │
                              ▼
                    ┌───────────────────┐
                    │   Layer 1: 🤖     │
                    │  AI Speaking?     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   YES   │   NO    │
                    └────┬────┴────┬────┘
                         │         │
                    ❌ BLOCK   ┌───▼──────────────┐
                         │     │   Layer 2: ⏳    │
                         │     │   In Cooldown?   │
                         │     └───────┬──────────┘
                         │             │
                         │   ┌─────────▼─────────┐
                         │   │  YES   │   NO     │
                         │   └───┬────┴────┬─────┘
                         │       │         │
                         │  ❌ BLOCK   ┌───▼──────────────┐
                         │       │     │   Layer 3: 📝    │
                         │       │     │   Duplicate?     │
                         │       │     └───────┬──────────┘
                         │       │             │
                         │       │   ┌─────────▼─────────┐
                         │       │   │  YES   │   NO     │
                         │       │   └───┬────┴────┬─────┘
                         │       │       │         │
                         │       │  ❌ BLOCK   ✅ DETECT
                         │       │       │         │
                         └───────┴───────┴─────────▼
                                        Emotion Detected!
                                        Trigger AI Response
```

---

## State Machine Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      🔄 DETECTION STATES                         │
└─────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────────────┐
        │         🟢 READY TO DETECT               │
        │  • AI not speaking                       │
        │  • No cooldown active                    │
        │  • Listening for emotions                │
        └──────────┬───────────────────────────────┘
                   │
                   │ User emotion detected
                   │
                   ▼
        ┌──────────────────────────────────────────┐
        │         🔴 COOLDOWN (5 seconds)          │
        │  • Blocking new detections               │
        │  • Can still hear audio                  │
        │  • Shows countdown in console            │
        └──────────┬───────────────────────────────┘
                   │
                   │ AI starts speaking
                   │
                   ▼
        ┌──────────────────────────────────────────┐
        │         🔵 AI SPEAKING                   │
        │  • Ignoring ALL input                    │
        │  • Cooldown still running                │
        │  • Waiting for AI to finish              │
        └──────────┬───────────────────────────────┘
                   │
                   │ AI finishes + cooldown expires
                   │
                   ▼
        ┌──────────────────────────────────────────┐
        │         🟢 READY TO DETECT               │
        │  (Back to start)                         │
        └──────────────────────────────────────────┘
```

---

## Event Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      📡 EVENT COMMUNICATION                      │
└─────────────────────────────────────────────────────────────────┘

WebSocketService          Window Events       AudioEmotionDetector
     (websocket.js)                              (Component)
         │                                            │
         │ audio.play()                              │
         ├───────────────────────────────────────────>│
         │  Emit: 'ai-speaking'                      │
         │  { speaking: true }                       │
         │                                            │
         │                                            │ isAISpeaking = true
         │                                            │ Pause detection
         │                                            │
         │ [AI audio playing...]                     │
         │                                            │
         │ User speaks: "wow"                        │
         │                                            ├─> ❌ BLOCKED
         │                                            │   (AI speaking)
         │                                            │
         │ audio.ended()                             │
         ├───────────────────────────────────────────>│
         │  Emit: 'ai-speaking'                      │
         │  { speaking: false }                      │
         │                                            │
         │                                            │ isAISpeaking = false
         │                                            │ Resume detection
         │                                            │
         │ User speaks: "haha"                       │
         │                                            ├─> ✅ DETECT
         │◄───────────────────────────────────────────┤   (If cooldown ok)
         │  Emotion: Happy                           │
         │                                            │
```

---

## Timeline Example

```
┌─────────────────────────────────────────────────────────────────┐
│                  ⏱️ REAL-TIME TIMELINE                          │
└─────────────────────────────────────────────────────────────────┘

Time  Event                              State           Detects?
────  ─────────────────────────────────  ──────────────  ────────
0:00  User: "haha"                       🟢 Ready        ✅ YES
0:00  → Emotion detected: Happy          🔴 Cooldown     
0:00  → AI starts responding                             
0:01  → AI speaking "What's so funny?"   🔵 AI Speaking  ❌ NO
0:02  User: "nothing" (tries to speak)   🔵 AI Speaking  ❌ NO
0:03  → AI continues speaking            🔵 AI Speaking  ❌ NO
0:04  → AI audio ends                    🔴 Cooldown     ❌ NO
0:05  → Cooldown expires                 🟢 Ready        ✅ YES
0:06  User: "wow"                        🟢 Ready        ✅ YES
0:06  → Emotion detected: Surprised      🔴 Cooldown     
0:07  User: "amazing" (too soon)         🔴 Cooldown     ❌ NO
0:11  → Cooldown expires                 🟢 Ready        ✅ YES
```

---

## Comparison Chart

```
┌─────────────────────────────────────────────────────────────────┐
│              📊 BEFORE vs AFTER COMPARISON                       │
└─────────────────────────────────────────────────────────────────┘

Feature                   Before ❌         After ✅
──────────────────────────────────────────────────────────────────
Detects User Emotions     ✅ Yes            ✅ Yes
Detects AI Voice          ❌ Yes (BUG!)     ✅ No (FIXED!)
Multiple Triggers         ❌ 5-10 times     ✅ Once only
Cooldown System           ❌ 2s (too short) ✅ 5s (balanced)
AI Speaking Detection     ❌ None           ✅ Full blocking
False Positives           ❌ High           ✅ Near zero
User Experience           ❌ Confusing      ✅ Natural
API Efficiency            ❌ Wasteful       ✅ Optimized
Conversation Flow         ❌ Broken         ✅ Smooth
──────────────────────────────────────────────────────────────────
```

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    🏗️ SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                        Frontend Layer                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              CameraView.vue (Parent)                    │  │
│  │  • Handles camera/face detection                        │  │
│  │  • Integrates child components                          │  │
│  │  • Manages overall emotion state                        │  │
│  └────────────────────────┬────────────────────────────────┘  │
│                           │                                    │
│          ┌────────────────┴────────────────┐                  │
│          │                                  │                  │
│  ┌───────▼────────────┐         ┌──────────▼────────────┐    │
│  │ MediaPipe          │         │ AudioEmotionDetector  │    │
│  │ Face Detection     │         │ • Microphone input    │    │
│  │ • Visual emotions  │         │ • Speech recognition  │    │
│  │ • 3s stability     │         │ • Volume detection    │    │
│  └────────────────────┘         │ • 5s cooldown        │    │
│                                  │ • AI speaking check   │    │
│                                  └──────────┬────────────┘    │
│                                             │                  │
└─────────────────────────────────────────────┼──────────────────┘
                                              │
                                              │ Events
                                              │
┌─────────────────────────────────────────────┼──────────────────┐
│                    WebSocket Layer          │                  │
│  ┌──────────────────────────────────────────▼────────────────┐ │
│  │                 WebSocketService                          │ │
│  │  • Real-time communication                                │ │
│  │  • Audio playback management                              │ │
│  │  • Emits 'ai-speaking' events ⭐ NEW                     │ │
│  │  • Tracks current audio state  ⭐ NEW                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Code Locations Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                   📁 FILE MODIFICATION MAP                       │
└─────────────────────────────────────────────────────────────────┘

File: frontend/src/services/websocket.js
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Line 16:   this.currentAudio = null;              [NEW]
Line 130:  Stop previous audio if playing         [NEW]
Line 147:  audio.addEventListener('play', ...)    [NEW]
Line 154:  audio.addEventListener('error', ...)   [UPDATED]
Line 160:  audio.addEventListener('ended', ...)   [UPDATED]
Line 167:  audio.addEventListener('pause', ...)   [NEW]

File: frontend/src/components/camera/AudioEmotionDetector.vue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Line 43:   import { onMounted }                   [UPDATED]
Line 60:   let lastEmotionTime = 0;               [NEW]
Line 61:   let isAISpeaking = false;              [NEW]
Line 62:   const DETECTION_COOLDOWN = 5000;       [NEW]
Line 160:  if (isAISpeaking) return;              [NEW]
Line 164:  if (duplicate) return;                 [NEW]
Line 239:  if (now - lastEmotionTime < ...) ...   [NEW]
Line 281:  if (isAISpeaking || cooldown) ...      [UPDATED]
Line 311:  const handleAISpeaking = ...           [NEW]
Line 320:  onMounted(() => ...)                   [NEW]
```

---

**Visual Guide Complete!** 🎨  
Use this for understanding the system architecture and debugging. ✨
