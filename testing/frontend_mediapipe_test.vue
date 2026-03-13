<!-- 
  =============================================
  MODULE 3: MediaPipe Telemetry Inject
  =============================================
  Purpose: Prove the response latency of gesture control for TC-01.
  
  Instructions:
  1. Open frontend/src/components/camera/CameraView.vue
  2. Locate the \`interpretGestures\` function block.
  3. Find the \`case 'Open_Palm':\` section.
  4. Replace that specific case block with the code below.
  5. Open Chrome DevTools Console (F12) to see the Timestamp A and B latency math when you do the gesture.
-->

    case 'Open_Palm':
      currentGesture.value = 'Open Palm';
      gestureIcon.value = '✋';
      if (now - lastGestureTime > GESTURE_COOLDOWN) {
        
        // ===== [TESTING INJECT: START Timestamp A] =====
        const timestampA = performance.now();
        console.log(`[TESTING] ✋ Open_Palm Gesture Recognized (Confidence > 0.6) at: ${timestampA.toFixed(2)}ms`);
        // ===============================================

        executeGestureAction('Stop AI', () => {
          console.log('✋ Gesture Triggered: Terminating AI Response');
          websocketService.terminateResponse();
          
          // ===== [TESTING INJECT: END Timestamp B] =====
          const timestampB = performance.now();
          const latencyDelta = timestampB - timestampA;
          
          console.log(`[TESTING] ⚡ websocketService.terminateResponse() executed at: ${timestampB.toFixed(2)}ms`);
          console.log(`[TESTING] ⏱️ ACTION LATENCY (Timestamp B - Timestamp A): ${latencyDelta.toFixed(2)}ms`);
          console.log(`[TESTING] 📊 TC-01 Evaluation Pass (<1000ms): ${latencyDelta < 1000 ? 'YES ✅' : 'NO ❌'}`);
          // ===============================================

          showToast('✋', 'AI response terminated');
        });
      }
      break;
