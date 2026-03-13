# ✅ Camera Feature Testing Checklist

## Pre-Testing Setup

- [ ] Backend server running (`python run.py`)
- [ ] Frontend dev server running (`npm run dev`)
- [ ] Browser: Chrome/Edge (recommended)
- [ ] Camera connected and working
- [ ] Good lighting in room
- [ ] Internet connection active (for first load)

---

## 1. Initial State Tests

### Test 1.1: Placeholder Display
- [ ] Open `http://localhost:5173`
- [ ] Navigate to right panel (camera area)
- [ ] Verify you see:
  - [ ] "CAMERA FEED" title
  - [ ] Pulsing camera icon 📹
  - [ ] "No active camera" status
  - [ ] Blue "Enable Camera" button
- [ ] Button is clickable and not disabled

**Expected**: Clean, professional placeholder UI

---

## 2. Camera Activation Tests

### Test 2.1: Model Loading
- [ ] Click "Enable Camera" button
- [ ] Verify status changes to "Loading AI model..."
- [ ] Button changes to "Loading..." and becomes disabled
- [ ] Wait 2-5 seconds
- [ ] Check console for: "✅ Face Landmarker loaded successfully!"

**Expected**: Smooth loading experience, no errors

### Test 2.2: Camera Permission
- [ ] Browser shows permission prompt
- [ ] Click "Allow" to grant camera access
- [ ] Verify camera light turns on
- [ ] Video feed appears (mirrored/selfie mode)
- [ ] Placeholder disappears

**Expected**: Video feed displays immediately after permission

### Test 2.3: Permission Denied
- [ ] Stop camera if active
- [ ] Reload page
- [ ] Click "Enable Camera"
- [ ] Click "Block" on permission prompt
- [ ] Verify alert: "Could not access the camera..."
- [ ] Button remains clickable (can retry)

**Expected**: Graceful error handling

---

## 3. Face Detection Tests

### Test 3.1: Face Detected
- [ ] Position face in camera view
- [ ] Verify within 2 seconds:
  - [ ] "● Face Detected" appears (green)
  - [ ] Status dot has breathing animation
  - [ ] Emotion badge shows "😐 NEUTRAL" or current emotion
- [ ] Check console: Detection logs appearing

**Expected**: Instant face detection with visual feedback

### Test 3.2: No Face
- [ ] Move out of camera view
- [ ] Verify within 1 second:
  - [ ] "○ No Face" appears (red)
  - [ ] Status dot blinks (no breathing)
  - [ ] Emotion shows "❓ No Face"
- [ ] Return to view
- [ ] Verify detection resumes

**Expected**: Clear indication when face is missing

---

## 4. Emotion Recognition Tests

### Test 4.1: Happy Emotion
- [ ] Face camera with neutral expression
- [ ] Smile widely (show teeth)
- [ ] Verify within 1 second:
  - [ ] Emotion badge updates to "😊 HAPPY"
  - [ ] Badge glows with cyan border
  - [ ] Console shows: "Emotion: happy"

**Expected**: Happy emotion detected accurately

### Test 4.2: Surprised Emotion
- [ ] Start with neutral face
- [ ] Open mouth wide (like saying "WOW!")
- [ ] Verify:
  - [ ] Emotion changes to "😲 SURPRISED"
  - [ ] Update is instant

**Expected**: Surprised detected when jaw opens

### Test 4.3: Blinking
- [ ] Close both eyes
- [ ] Hold for 1 second
- [ ] Verify: "😌 BLINKING" appears briefly
- [ ] Open eyes
- [ ] Returns to previous emotion

**Expected**: Blinking detected during eye closure

### Test 4.4: Neutral Expression
- [ ] Relax face (no smile, no frown)
- [ ] Verify: "😐 NEUTRAL" appears
- [ ] This should be default state

**Expected**: Neutral is default emotion

### Test 4.5: Rapid Emotion Changes
- [ ] Smile → Neutral → Surprised → Smile
- [ ] Change every 2 seconds
- [ ] Verify all changes detected
- [ ] No lag or freezing

**Expected**: Smooth transitions, all emotions caught

---

## 5. UI/UX Tests

### Test 5.1: Emotion Badge Styling
- [ ] Verify emotion badge has:
  - [ ] Large emoji (2rem)
  - [ ] Uppercase emotion text
  - [ ] Cyan glowing border
  - [ ] Semi-transparent dark background
  - [ ] Cyberpunk clipped corners
  - [ ] Slide-up animation on appear

**Expected**: Professional cyberpunk aesthetic

### Test 5.2: Detection Status Styling
- [ ] Face detected:
  - [ ] Green text and border
  - [ ] Dot has breathing animation
  - [ ] Cyan glow effect
- [ ] No face:
  - [ ] Red text and border
  - [ ] Dot blinks
  - [ ] No glow

**Expected**: Clear visual distinction between states

### Test 5.3: Stop Camera Button
- [ ] Verify button is visible
- [ ] Has red theme
- [ ] Icon + "STOP CAMERA" text
- [ ] Hover: slides right and glows
- [ ] Click feel: smooth

**Expected**: Obvious danger/stop action

---

## 6. Stop Camera Tests

### Test 6.1: Normal Stop
- [ ] Click "Stop Camera" button
- [ ] Verify immediately:
  - [ ] Video feed stops
  - [ ] Camera light turns off
  - [ ] Emotion overlay disappears
  - [ ] Placeholder returns
  - [ ] "Enable Camera" button is back
- [ ] Check console: "🛑 Camera stopped"

**Expected**: Clean shutdown, no lingering processes

### Test 6.2: Restart Camera
- [ ] Stop camera (from test above)
- [ ] Wait 2 seconds
- [ ] Click "Enable Camera" again
- [ ] Verify:
  - [ ] No model re-download (cached)
  - [ ] Camera starts faster (~1 second)
  - [ ] Detection resumes immediately

**Expected**: Fast restart using cached model

---

## 7. Performance Tests

### Test 7.1: Frame Rate
- [ ] Open DevTools (F12)
- [ ] Go to Performance tab
- [ ] Start recording
- [ ] Let camera run for 10 seconds
- [ ] Stop recording
- [ ] Check FPS: Should be 25-30 FPS

**Expected**: Consistent frame rate, no drops

### Test 7.2: CPU Usage
- [ ] Open Task Manager (Ctrl+Shift+Esc)
- [ ] Find browser process
- [ ] With camera active, check CPU:
  - [ ] GPU mode: 10-20%
  - [ ] CPU mode: 40-60%

**Expected**: Reasonable CPU usage

### Test 7.3: Memory Usage
- [ ] Check Task Manager
- [ ] Memory for browser tab:
  - [ ] Before camera: ~100-150MB
  - [ ] After camera: ~200-300MB
  - [ ] No memory leaks over 5 minutes

**Expected**: Stable memory, no continuous growth

---

## 8. Edge Case Tests

### Test 8.1: Poor Lighting
- [ ] Turn off lights or cover camera partially
- [ ] Verify:
  - [ ] Detection may fail
  - [ ] Shows "No Face" status
  - [ ] No crashes or errors

**Expected**: Graceful degradation

### Test 8.2: Multiple Faces
- [ ] Have 2 people in view
- [ ] Verify:
  - [ ] Detects one face (closest/clearest)
  - [ ] No crashes
  - [ ] Emotion updates for detected face

**Expected**: Single face tracking (by design)

### Test 8.3: Extreme Angles
- [ ] Tilt head 90° (sideways)
- [ ] Verify:
  - [ ] May lose detection
  - [ ] Shows "No Face"
  - [ ] Resume when face returns to normal

**Expected**: Detection works best at normal angles

### Test 8.4: Covered Face
- [ ] Wear sunglasses or mask
- [ ] Verify:
  - [ ] Detection may still work
  - [ ] Emotions may be less accurate
  - [ ] No crashes

**Expected**: Reduced accuracy but still functional

### Test 8.5: Fast Movements
- [ ] Move head quickly left-right
- [ ] Verify:
  - [ ] Detection tracks smoothly
  - [ ] No jitter or lag
  - [ ] Face re-detected after movement

**Expected**: Smooth tracking

---

## 9. Browser Compatibility Tests

### Test 9.1: Chrome/Edge
- [ ] Test in Chrome
- [ ] All features work perfectly
- [ ] GPU acceleration active
- [ ] Best performance

**Expected**: Full compatibility (recommended browser)

### Test 9.2: Firefox
- [ ] Test in Firefox
- [ ] All features work
- [ ] Slightly lower performance acceptable

**Expected**: Working but may be slower

### Test 9.3: Safari (if available)
- [ ] Test in Safari
- [ ] Basic functionality works
- [ ] May have quirks

**Expected**: Partial support

---

## 10. Error Handling Tests

### Test 10.1: No Internet (First Load)
- [ ] Disconnect internet
- [ ] Clear browser cache
- [ ] Try to enable camera
- [ ] Verify: Error message about model loading
- [ ] Re-connect internet
- [ ] Retry successfully

**Expected**: Clear error message

### Test 10.2: No Internet (Cached)
- [ ] Load page with internet
- [ ] Enable camera once (cache model)
- [ ] Disconnect internet
- [ ] Stop and restart camera
- [ ] Verify: Still works (uses cache)

**Expected**: Works offline after first load

### Test 10.3: Camera Busy
- [ ] Open Zoom/Teams (or any app using camera)
- [ ] Try to enable camera in app
- [ ] Verify: Error about camera access
- [ ] Close other app
- [ ] Retry successfully

**Expected**: Helpful error message

---

## 11. Console Log Tests

### Test 11.1: Expected Logs
When camera is activated, verify these logs appear:
```
📷 Camera component mounted
🔄 Initializing MediaPipe Face Landmarker...
✅ Face Landmarker loaded successfully!
✅ Camera enabled and detection started
```

When face is detected:
```
🎭 Character emotion changed to: [emotion]
```

When camera stops:
```
🛑 Camera stopped
🧹 Cleaning up camera component
```

**Expected**: Clean, informative logging

### Test 11.2: No Error Logs
- [ ] Check console for:
  - [ ] No uncaught errors
  - [ ] No warnings (except npm audit)
  - [ ] No failed network requests

**Expected**: Clean console (errors = problems)

---

## 12. Integration Tests (Optional)

### Test 12.1: With Backend Running
- [ ] Backend server running
- [ ] Camera active
- [ ] Send chat message
- [ ] Verify:
  - [ ] Camera still works
  - [ ] No interference
  - [ ] Both features work independently

**Expected**: No conflicts between features

### Test 12.2: With Character View
- [ ] 3D character visible (center panel)
- [ ] Camera active (right panel)
- [ ] Verify:
  - [ ] Both render smoothly
  - [ ] No performance issues
  - [ ] CPU/GPU usage acceptable

**Expected**: Both features coexist well

---

## 13. Mobile/Responsive Tests (Optional)

### Test 13.1: Tablet View
- [ ] Resize browser to ~1024px width
- [ ] Verify camera panel still visible
- [ ] All buttons accessible
- [ ] Text readable

**Expected**: Responsive layout

### Test 13.2: Mobile View
- [ ] Resize to ~375px width
- [ ] Check if camera panel adapts
- [ ] May need scrolling (acceptable)

**Expected**: Functional on mobile (best effort)

---

## 14. Stress Tests

### Test 14.1: Long Duration
- [ ] Enable camera
- [ ] Leave running for 5 minutes
- [ ] Verify:
  - [ ] No performance degradation
  - [ ] Memory stable
  - [ ] Detection still accurate

**Expected**: Stable over time

### Test 14.2: Multiple Start/Stop Cycles
- [ ] Enable camera
- [ ] Stop camera
- [ ] Repeat 10 times
- [ ] Verify:
  - [ ] No memory leaks
  - [ ] Each cycle works
  - [ ] No slowdown

**Expected**: Clean resource management

---

## 15. Final Verification

### Checklist Before Production
- [ ] All emotion types detected correctly
- [ ] UI looks professional and polished
- [ ] No console errors
- [ ] Performance acceptable (25+ FPS)
- [ ] Stop button works reliably
- [ ] Camera releases properly on stop
- [ ] Model loads and caches correctly
- [ ] Error messages are helpful
- [ ] Works in primary browsers (Chrome/Edge)
- [ ] Documentation is complete

---

## Bug Report Template

If you find an issue:

```
**Bug Title**: [Short description]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Browser**: Chrome/Firefox/Safari [version]
**OS**: Windows/Mac/Linux
**Console Errors**: [Copy from F12 console]
**Screenshot**: [If visual issue]
```

---

## Test Results Summary

After completing all tests, fill this out:

```
Date Tested: __________
Tester Name: __________

Total Tests: 60+
Passed: _____ / 60
Failed: _____ / 60

Critical Issues Found: _____
Minor Issues Found: _____

Overall Status: ✅ PASS / ❌ FAIL

Notes:
[Any observations or concerns]
```

---

## Performance Benchmarks

Target metrics:

| Metric | Target | Actual | Pass? |
|--------|--------|--------|-------|
| Model Load Time | < 5s | ____ | ☐ |
| Camera Start Time | < 2s | ____ | ☐ |
| Detection FPS | 25-30 | ____ | ☐ |
| CPU Usage (GPU) | < 20% | ____ | ☐ |
| Memory Usage | < 300MB | ____ | ☐ |
| Face Detection Lag | < 100ms | ____ | ☐ |
| Emotion Update Lag | < 200ms | ____ | ☐ |

---

**Last Updated**: October 8, 2025  
**Version**: 1.0.0  
**Purpose**: Comprehensive testing guide
