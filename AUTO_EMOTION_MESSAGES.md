# 🤖 Auto Emotion Messages Feature

## Overview

The camera now automatically sends **hidden messages** to the AI when it detects stable emotions, prompting the AI to respond naturally without the trigger message appearing in chat.

---

## 🎯 How It Works

### Detection Flow

```
Camera Detects Emotion (3+ seconds stable)
    ↓
Hidden Message Sent to AI
    ↓
AI Generates Response
    ↓
Response Appears in Chat (with voice)
    ↓
User sees only AI's question/comment
```

---

## 😊 Emotion Triggers

### 1. **Happy** 
**When**: You smile for 3+ seconds  
**Hidden Prompt**: *"I notice the user seems very happy right now! Ask them warmly what made them so happy today."*  
**AI Response Example**: *"You seem really happy! What's making you smile today?"*

### 2. **Sad** 😢
**When**: You frown for 3+ seconds  
**Hidden Prompt**: *"The user appears to be feeling down. Ask them gently if everything is okay and if they want to talk about it."*  
**AI Response Example**: *"I notice you seem a bit down. Is everything okay? Want to talk about it?"*

### 3. **Angry** 😠
**When**: You show anger for 3+ seconds  
**Hidden Prompt**: *"The user seems frustrated or angry. Ask them calmly what's bothering them and offer support."*  
**AI Response Example**: *"You look frustrated. What's bothering you? I'm here to listen."*

### 4. **Surprised** 😲
**When**: You show surprise for 3+ seconds  
**Hidden Prompt**: *"The user looks surprised! Ask them curiously what caught their attention or surprised them."*  
**AI Response Example**: *"Wow, you look surprised! What happened?"*

---

## ⚙️ Feature Settings

### Stability Check
- **Requirement**: Emotion must be stable for **10 consecutive frames** (~3 seconds at 30 FPS)
- **Purpose**: Prevents false triggers from brief expressions

### Cooldown Period
- **Duration**: 30 seconds per emotion
- **Purpose**: Prevents AI from repeatedly asking the same question

### Confidence Threshold
- **Minimum**: 35% confidence required
- **Purpose**: Only trigger on clear, strong emotions

---

## 📊 What You'll See

### In Chat UI
```
[Camera detects you're happy]

AI: "You seem really happy! What's making you smile today?" 🎤

[Only AI's message appears - your emotion trigger is hidden]
```

### In Console (F12)
```
🎭 Detected: Happy (confidence: 45%)
📤 Sending hidden emotion prompt: Happy
💡 AI noticed you're happy and will ask about it!
🔒 Hidden message (won't appear in chat UI)
🤖 AI Response: You seem really happy! What's making you...
```

---

## 🎮 User Experience

### Scenario 1: Happy Moment
1. You receive good news and smile
2. Camera detects stable happiness (3 seconds)
3. AI suddenly asks: *"You look happy! What's going on?"*
4. You can respond naturally
5. Feels like AI is genuinely noticing your mood!

### Scenario 2: Feeling Down
1. You're having a bad day, looking sad
2. Camera detects sadness
3. AI gently asks: *"Are you okay? Want to talk?"*
4. Supportive conversation begins

---

## 🔧 Customization

### Adjust Stability Time

Edit `CameraView.vue` line ~25:
```javascript
const EMOTION_DURATION_THRESHOLD = 3000; // Change to 2000 for faster (2s)
```

### Adjust Stability Frames

Edit `CameraView.vue` line ~27:
```javascript
const EMOTION_HISTORY_SIZE = 10; // Change to 15 for more stable (5s at 30fps)
```

### Change Prompts

Edit `CameraView.vue` line ~200:
```javascript
const emotionMessages = {
  'Happy': "Your custom prompt here",
  'Sad': "Your custom prompt here",
  // ...
};
```

### Add New Emotions

```javascript
const emotionMessages = {
  'Happy': "...",
  'Sad': "...",
  'Angry': "...",
  'Surprised': "...",
  'Excited': "User is very excited! Ask them what's happening!",  // NEW
};
```

---

## 🧪 Testing

### Test Happy Trigger
1. Enable camera
2. Smile widely for 3 seconds
3. Keep smiling steadily (don't break expression)
4. After 3 seconds, AI should ask about your happiness
5. Check console for: `📤 Sending hidden emotion prompt: Happy`

### Test Cooldown
1. Trigger happy emotion
2. Wait for AI response
3. Smile again immediately
4. Nothing should happen (30-second cooldown)
5. Wait 30 seconds and try again → Should work

### Test Stability
1. Smile for 1 second → Stop → Smile again
2. Should NOT trigger (not stable enough)
3. Smile continuously for 3+ seconds
4. Should trigger successfully

---

## 💡 Best Practices

### For Users
1. **Hold Expression**: Keep emotion for 3+ seconds
2. **Be Natural**: Don't force expressions
3. **Good Lighting**: Better detection = faster triggers
4. **Face Camera**: Direct view works best

### For Developers
1. **Adjust Thresholds**: Tune based on user feedback
2. **Test Prompts**: Ensure AI responses sound natural
3. **Monitor Logs**: Check for false triggers
4. **Balance Frequency**: Not too annoying, not too rare

---

## 🎨 Advanced: Custom Behaviors

### Emotion Combinations
```javascript
// Example: Detect sustained happiness → Excitement
if (detectedEmotion === 'Happy' && confidence > 0.7) {
  sendHiddenEmotionMessage('Excited');
}
```

### Time-Based Triggers
```javascript
// Example: Morning greeting for happy users
const hour = new Date().getHours();
if (emotion === 'Happy' && hour < 12) {
  message = "Good morning! You're starting the day with a smile!";
}
```

### Context-Aware Messages
```javascript
// Example: Different prompts based on conversation history
const recentMessages = chatStore.messages.slice(-5);
if (recentMessages.some(m => m.text.includes('exam'))) {
  message = "You look happy! Did the exam go well?";
}
```

---

## 🐛 Troubleshooting

### AI Not Responding to Emotions

**Check**:
1. Camera is enabled
2. Face is detected (green indicator)
3. Emotion is stable for 3 seconds
4. Console shows `📤 Sending hidden emotion prompt`
5. Backend is running

**Solution**: Check WebSocket connection and backend logs

### Too Many Triggers

**Problem**: AI keeps asking about emotions

**Solution**: Increase cooldown period
```javascript
setTimeout(() => {
  lastEmotionSent = '';
}, 60000); // 60 seconds instead of 30
```

### Not Enough Triggers

**Problem**: AI rarely notices emotions

**Solution**: Lower confidence threshold
```javascript
if (confidence < 0.25) return; // 25% instead of 35%
```

---

## 📈 Analytics Ideas

Track emotion triggers:
```javascript
const emotionStats = {
  happy: 0,
  sad: 0,
  angry: 0,
  surprised: 0
};

// In sendHiddenEmotionMessage()
emotionStats[emotion.toLowerCase()]++;
console.log('📊 Emotion Stats:', emotionStats);
```

---

## 🔮 Future Enhancements

### Possible Additions
1. **Multi-emotion sequences**: "You went from surprised to happy!"
2. **Mood tracking**: "You've been smiling a lot today!"
3. **Personalized responses**: Learn user's typical emotions
4. **Gesture triggers**: Wave → AI greets you
5. **Time-based context**: Different responses for morning/evening

---

## 🎉 Benefits

### User Benefits
- ✨ More natural, empathetic AI
- 🤗 Feels like AI "gets" you
- 💬 Spontaneous conversations
- 🎭 Emotion-aware interactions

### Developer Benefits
- 🔧 Easy to customize
- 📊 Can track user emotions
- 🎮 Creates engaging UX
- 🚀 Differentiates your app

---

## 📝 Code Summary

### Frontend (CameraView.vue)
```javascript
// Detects emotion → Checks stability → Sends hidden message
checkAndSendEmotionMessage(emotion, confidence)
  ↓
sendHiddenEmotionMessage(emotion)
  ↓
websocketService.sendMessage({ text: prompt, hidden: true })
```

### Backend (websockets.py)
```python
# Receives hidden message → Generates AI response → Sends back
is_hidden = message_data.get("hidden", False)
  ↓
ai_response = gemini_service.generate_response(message_text, user_id)
  ↓
await manager.send_personal_json(ai_response, websocket)
```

### Chat Store (chatStore.js)
```javascript
// Filters out hidden user messages from UI
if (message.hidden) {
  return; // Don't show in chat
}
```

---

## ✅ Feature Status

- [x] Emotion detection
- [x] Stability checking
- [x] Hidden message sending
- [x] Cooldown system
- [x] Backend processing
- [x] AI response generation
- [x] Voice synthesis
- [x] UI filtering

**Status**: ✅ Ready for use!

---

**Created**: October 8, 2025  
**Version**: 1.0.0  
**Purpose**: Automatic emotion-triggered AI conversations
