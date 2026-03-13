# 🧪 Quick Test Guide - Audio Detection Fix

## What Was The Problem?
When AI spoke multiple lines, the microphone detected the AI's voice coming from speakers, causing repeated emotion detections.

## What Was Fixed?
Added 3-layer protection:
1. **AI Speaking Detection** - Pauses emotion detection when AI is talking
2. **5-Second Cooldown** - Prevents rapid consecutive detections  
3. **Transcript Deduplication** - Filters duplicate voice inputs

---

## 🚀 How to Test

### Step 1: Reload Frontend
```bash
Ctrl + F5 (hard refresh)
```
Or close and reopen the browser tab.

### Step 2: Enable Camera + Microphone
1. Click "Enable Camera"
2. Click "Mic: OFF" to turn it ON
3. Grant permissions

### Step 3: Test Single Detection ✅
**Do**: Say "haha" once  
**Expected**:
- Console shows: `🔊 Detected laughter: "haha" → Happy`
- AI responds asking what's funny
- Console shows: `🔊 AI started speaking`
- Console shows: `🤐 Pausing emotion detection - AI is speaking`

**Success**: Only ONE detection, AI speaks without triggering more

---

### Step 4: Test During AI Speech 🛡️
**Do**: While AI is speaking, say "wow" or "haha"  
**Expected**:
- Console shows: `🤖 AI is speaking, skipping detection`
- NO emotion detected
- NO new AI response triggered

**Success**: Your voice is ignored while AI speaks

---

### Step 5: Test Cooldown ⏳
**Do**: Say "haha" twice within 5 seconds  
**Expected**:
- First "haha": Detected ✅
- Second "haha": Console shows `⏳ Cooldown active: 3s remaining`
- Second one is ignored

**Success**: Only first detection counts, rest blocked by cooldown

---

### Step 6: Test After Cooldown ✅
**Do**: 
1. Say "haha" (triggers detection)
2. Wait for AI to finish speaking
3. Wait 5 seconds total
4. Say "wow"

**Expected**:
- First "haha": Detected ✅
- "wow" after 5s: Detected ✅
- Both trigger separate AI responses

**Success**: After cooldown expires, detection resumes normally

---

## 📊 What to Look For in Console

### ✅ Good Output (Working)
```
🎤 Heard: haha
🔊 Detected laughter: "haha" → Happy
📤 Sending hidden emotion prompt (🎤 Audio): Happy
🔊 AI started speaking
🤐 Pausing emotion detection - AI is speaking

[You say something during AI response]
🤖 AI is speaking, skipping detection

✅ Audio playback complete
👂 Resuming emotion detection - AI finished speaking
```

### ❌ Bad Output (Bug Still Exists)
```
🎤 Heard: haha
🔊 Detected laughter → Happy
🔊 Detected again → Happy  ❌ DUPLICATE!
🔊 Detected again → Happy  ❌ DUPLICATE!
[Multiple detections = bug not fixed]
```

---

## 🎯 Success Criteria

- [ ] **Single Detection**: Say "haha" → Only ONE detection
- [ ] **No AI Voice Detection**: AI speaks → No emotions detected from AI voice
- [ ] **Cooldown Works**: Rapid sounds → Only first one detected
- [ ] **Resume After AI**: AI finishes → Can detect again immediately
- [ ] **Cooldown Expires**: Wait 5s → Next emotion detected successfully

---

## 🐛 If Still Having Issues

### Multiple Detections During AI Speech?
**Try**:
1. Check console for "🔊 AI started speaking" message
2. If missing, reload page with Ctrl+F5
3. Try using headphones (prevents speaker feedback)

### No Detection After AI Speaks?
**Try**:
1. Check console for "✅ Audio playback complete"
2. If stuck in "AI speaking" state, reload page
3. May need to re-enable microphone

### Cooldown Too Long/Short?
**Edit**: Open `AudioEmotionDetector.vue`, line 62:
```javascript
const DETECTION_COOLDOWN = 5000; // Change to 3000 for 3s
```

---

## 🎉 Expected Result

**Before Fix**:
- User laughs → AI responds → AI's voice triggers → AI responds again → Loop! 💥

**After Fix**:
- User laughs → AI responds → AI voice ignored ✅ → Clean conversation flow 🎯

---

## Quick Command Reference

### Reload Frontend
```bash
# In browser
Ctrl + F5
```

### Check Console
```bash
# In browser
F12 → Console tab
```

### Filter Console Logs
```
In console filter box, type: emotion
Shows only emotion-related logs
```

---

**Ready to test!** Just reload the page and try saying "haha" - you should see it detect once, then pause during AI speech. ✨
