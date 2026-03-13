<!--
  =============================================
  MODULE 4: Three.js FPS Stress Test Inject
  =============================================
  Purpose: Prove performance gain of Raycasting Invisible Bounding Box vs VRM High-Poly Mesh for TC-04.

  Instructions:
  1. To monitor FPS, open DevTools -> Rendering -> Check "Frame Rendering Stats" (or use a Vue/Three stats.js plugin).
  2. Open frontend/src/views/DesktopPetView.vue.
  3. Paste this function anywhere in your \`<script setup>\` script area.
  4. Call the function from your DevTools console or map it to a temporary button:
     - \`runRaycastStressTest(false)\` // Scenario A: Test against full character Mesh.
     - \`runRaycastStressTest(true)\`  // Scenario B: Test against optimized Box.
  5. Compare the FPS drops during the 10-second test window.
-->

// Paste this anywhere in DesktopPetView.vue's script:
const runRaycastStressTest = (useOptimizedBoundingBox = true) => {
    console.log(`[TESTING] 🚀 Starting 60Hz Raycast Stress Test...`);
    console.log(`[TESTING] 🎯 Target: ${useOptimizedBoundingBox ? 'Invisible Bounding Box (Optimized)' : 'Full VRM Mesh (Unoptimized)'}`);
    
    let totalHits = 0;
    const testDurationMs = 10000; // Run for 10 seconds
    const intervalMs = 1000 / 60; // 60 times a second

    // Expose temporarily to window if you want to call it from Chrome Console
    window._stressTestRunning = true;

    const interval = setInterval(() => {
        if (!camera || !scene) return;
        
        // Generate random screen coordinates to simulate chaos clicking
        mouseVec.x = (Math.random() * 2) - 1;
        mouseVec.y = (Math.random() * 2) - 1;
        raycaster.setFromCamera(mouseVec, camera);
        
        // Define raycasting target
        const target = useOptimizedBoundingBox ? clickBoundingBox : characterWrapperGroup;
        const recursive = !useOptimizedBoundingBox; // If using full mesh, we must recursively check children
        
        if (target) {
            // This is the heavy calculation!
            const intersects = raycaster.intersectObject(target, recursive);
            if (intersects.length > 0) {
                totalHits++;
            }
        }
    }, intervalMs); 
    
    // Stop after duration
    setTimeout(() => {
        clearInterval(interval);
        window._stressTestRunning = false;
        console.log(`[TESTING] ✅ Stress test completed.`);
        console.log(`[TESTING] 📊 Total virtual clicks processed: 600`);
        console.log(`[TESTING] 🎯 Total successful hits: ${totalHits}`);
        console.log(`[TESTING] 📝 Please log your minimal FPS seen during the test for the Chapter 6 report.`);
    }, testDurationMs);
};

// Expose to window immediately so you can trigger it from F12 Console:
// (Paste this inside onMounted)
// window.runRaycastStressTest = runRaycastStressTest;
