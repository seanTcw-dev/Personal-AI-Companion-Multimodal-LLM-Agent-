<template>
  <div class="signin-page">
    <!-- Animated 3D Grid Floor -->
    <canvas ref="gridCanvas" class="grid-canvas"></canvas>
    
    <!-- Floating Particles -->
    <canvas ref="particlesCanvas" class="particles-canvas"></canvas>
    
    <!-- Vignette Overlay -->
    <div class="vignette"></div>
    
    <div class="signin-container" v-if="!isLinkStart">
      <!-- Logo/Branding -->
      <div class="brand-header">
        <h1 class="brand-title">VirtuAI<br/>Companion</h1>
        <p class="brand-subtitle">Your AI-Powered Virtual Assistant</p>
      </div>
      
      <!-- Glassmorphism Card with Chamfered Corners -->
      <div class="signin-card">
        <!-- Chamfered Corner Overlays -->
        <div class="chamfer chamfer-tl"></div>
        <div class="chamfer chamfer-tr"></div>
        <div class="chamfer chamfer-bl"></div>
        <div class="chamfer chamfer-br"></div>
        
        <!-- Login Options -->
        <div class="login-options">
          <div class="tech-frame">
            <button @click="handleGoogleLogin" class="btn-google">
              <svg class="google-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </button>
          </div>
          
          <div class="divider">
            <span>OR</span>
          </div>
          
          <div class="tech-frame">
            <button @click="showGuestWarning" class="btn-guest">
              Continue as Guest
            </button>
          </div>
        </div>
        
        <p class="terms">
          By continuing, you agree to our Terms of Service.
        </p>
        
        <div class="back-link">
          <router-link to="/">← Return to Main Menu</router-link>
        </div>

        <!-- Pink Border Animation -->
        <div class="border-animation">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <!-- LINK START ANIMATION CONTAINER -->
    <div v-else class="link-start-container">
      <div class="link-content">
        <div class="verified-badge" v-if="linkStartPhase >= 1">
          <div class="check-icon">✓</div>
        </div>
        <h2 class="link-text" :class="{ 'glitch-text': linkStartPhase === 3 }">{{ linkStartText }}</h2>
        <div class="loading-bar-container" v-if="linkStartPhase === 2">
           <div class="loading-bar"></div>
        </div>
      </div>
      
      <!-- Warp Lines (High Speed Effect) -->


      <!-- White flash overlay -->
      <div class="white-flash" :class="{ 'active': linkStartPhase === 4 }"></div>
    </div>



    <!-- Guest Warning Modal -->
    <div v-if="showWarning" class="modal-overlay" @click.self="showWarning = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>⚠️ GUEST ACCESS RESTRICTED</h3>
        </div>
        <p class="warning-text">Warning: Unidentified User Detected.</p>
        <ul class="restriction-list">
          <li>Google Services Unavailable (Calendar, Gmail)</li>
          <li>Cloud Save Disabled</li>
          <li>Personalization Limited</li>
        </ul>
        <div class="modal-actions">
          <button @click="proceedAsGuest" class="btn-confirm">Proceed Anyway</button>
          <button @click="showWarning = false" class="btn-cancel">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const showWarning = ref(false);
const gridCanvas = ref(null);
const particlesCanvas = ref(null);
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

let googleClient = null;
const isLinkStart = ref(false);
const linkStartPhase = ref(0); // 0: Hidden, 1: Verified, 2: Initializing, 3: Link Start
const linkStartText = ref('');
let gridSpeed = 1; // Animation speed multiplier
let gridAnimationId = null;
let particlesAnimationId = null;

// Tunnel Transition State
const tunnelProgress = ref(0); // 0 = Flat, 1 = Full Tunnel
const cameraRotation = ref(0); // Rotation angle in radians





// Animated 3D Grid Floor
const initGridAnimation = () => {
  const canvas = gridCanvas.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  let offset = 0;
  const gridSize = 50;
  // Make perspective reactive to speed (Base 300)
  let currentPerspective = 300; 
  
  const drawGrid = () => {
    // Clear canvas
    ctx.fillStyle = tunnelProgress.value > 0.1 ? '#000000' : 'clear'; // Fade to black for tunnel
    if (tunnelProgress.value > 0.1) ctx.fillRect(0, 0, canvas.width, canvas.height);
    else ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height * 0.5;
    const maxLines = 40;
    
    // Animate offset with exponential speed
    offset += gridSpeed;
    if (offset > gridSize) offset = offset % gridSize;

    // Dynamic FOV/Distortion logic:
    // As speed increases, perspective decreases (wider FOV feeling) or increases?
    // Actually, "Warp" feel usually means high FOV. 
    // Let's modulate perspective based on gridSpeed.
    // Normal speed ~1. Max Speed ~200+
    // Base Perspective 300. At max speed, drag it down to create "fisheye" or up?
    // Let's try: Higher speed = Lower perspective value (draws things smaller/further, but wider angle technically)
    const targetPerspective = 300 - (Math.min(gridSpeed, 200) * 0.8);
    // Smooth lerp
    currentPerspective += (targetPerspective - currentPerspective) * 0.1;

    // Save context for rotation
    ctx.save();
    
    // Apply Camera Rotation in Tunnel Mode
    if (tunnelProgress.value > 0) {
      ctx.translate(cx, cy);
      ctx.rotate(cameraRotation.value);
      ctx.translate(-cx, -cy);
    }
    
    // Increase line width for impact
    ctx.lineWidth = 1 + (tunnelProgress.value * 3) + (gridSpeed * 0.05); // Thicker at high speed

    // --- DRAWING FUNCTION ---
    // We map a grid point (i, j) to screen coordinates (x, y)
    // i = horizontal index (left to right)
    // j = depth index (close to far)

    // Helper: Project 3D point to 2D
    const project = (x, y, z) => {
      const scale = currentPerspective / (z || 0.1);
      return {
        x: cx + (x * scale),
        y: cy + (y * scale),
        scale: scale
      };
    };

    // 1. LATITUDE LINES (Horizontal on floor -> Rings in tunnel)
    for (let j = 0; j < maxLines; j++) {
      // Z-depth calc
      const z = (j * gridSize) - offset + (gridSize * 2); // Start a bit deeper
      if (z < 1) continue;
      
      const alpha = Math.max(0, 1 - (z / 1000));
      
      ctx.beginPath();
      
      // We draw a line strip across the width
      const segments = 40; 
      for (let i = 0; i <= segments; i++) {
        // Normalized X from -1 to 1
        const u = (i / segments - 0.5) * 2; 
        
        // FLAT STATE:
        // x = u * width
        // y = floor_height (constant relative to horizon)
        const flatX = u * canvas.width * 2; 
        const flatY = 200; // units below horizon

        // TUNNEL STATE:
        // angle = u * PI (semicircle) or 2PI (full circle)
        // x = cos(angle) * radius
        // y = sin(angle) * radius
        const angle = u * Math.PI * 2; // Full circle
        const radius = 300;
        const tunnelX = Math.cos(angle) * radius;
        const tunnelY = Math.sin(angle) * radius;

        // Interpolate
        const t = tunnelProgress.value;
        const x3d = flatX * (1 - t) + tunnelX * t;
        const y3d = flatY * (1 - t) + tunnelY * t;
        
        // Project
        const p = project(x3d, y3d, z);
        
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      
      // Color: Cyan in tunnel, Blueish on floor
      const r = 0;
      const g = 180 + (tunnelProgress.value * 70); // Brighter cyan
      const b = 255;
      
      ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
      ctx.stroke();
    }

    // 2. LONGITUDE LINES (Vertical on floor -> Lengthwise in tunnel)
    for (let i = -15; i <= 15; i++) {
        // Normalized U based on index (-1 to 1 approx)
        const u = i / 10;
        
        ctx.beginPath();
        for (let j = 0; j < maxLines; j++) {
            const z = (j * gridSize) - offset + (gridSize * 2);
            if (z < 1) continue;

             // FLAT STATE
            const flatX = u * canvas.width * 1.5;
            const flatY = 200;

            // TUNNEL STATE
            const angle = u * Math.PI; // Semicircle + wrap
            // Twist vertical lines into radial lines
            // We map 'u' to an angle around the cylinder
            // To make them meet, we spread i over 0..2PI
            const tunnelAngle = (i / 15) * Math.PI * 2; 
            const radius = 300;
            const tunnelX = Math.cos(tunnelAngle) * radius;
            const tunnelY = Math.sin(tunnelAngle) * radius;

            // Interpolate
            const t = tunnelProgress.value;
            // For flat floor, we only want -1 to 1. For tunnel, we want full circle.
            // When t=0, use flat logic. When t=1, use tunnel logic.
            // We blend the *logic* of coordinate generation.
            
            let currentX, currentY;
            
            if (t < 1) {
                 // Hybrid Blend
                 // Linearly interpolate point positions?
                 // Flat X is linear. Tunnel X is radial.
                 // We simply lerp the final 3D coords.
                 const tx = Math.cos((i/15) * Math.PI * 2) * radius;
                 const ty = Math.sin((i/15) * Math.PI * 2) * radius;
                 
                 const fx = (i * gridSize * 3);
                 const fy = 200;
                 
                 currentX = fx * (1-t) + tx * t;
                 currentY = fy * (1-t) + ty * t;
            } else {
                 currentX = Math.cos((i/15) * Math.PI * 2) * radius;
                 currentY = Math.sin((i/15) * Math.PI * 2) * radius;
            }

            const p = project(currentX, currentY, z);
            
            if (j === 0) ctx.moveTo(p.x, p.y);
            else ctx.lineTo(p.x, p.y);
        }
        
        const alpha = 0.3 + (tunnelProgress.value * 0.4);
        ctx.strokeStyle = `rgba(0, 243, 255, ${alpha})`;
        ctx.stroke();
    }
    
    // Draw "Exit Light" Bloom in center
    if (tunnelProgress.value > 0.5) {
        const bloomSize = (tunnelProgress.value - 0.5) * 300; 
        const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, bloomSize * 4);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.2, 'rgba(0, 243, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        
        ctx.fillStyle = gradient;
        ctx.globalCompositeOperation = 'screen';
        ctx.beginPath();
        // Draw the bloom *without* rotation affecting its orientation (it's circular anyway)
        // But we must restore context first if we want it strictly screen-aligned? 
        // Actually circular bloom is fine rotated.
        ctx.arc(cx, cy, bloomSize * 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalCompositeOperation = 'source-over';
    }

    ctx.restore(); // Restore context (undo rotation)
    
    gridAnimationId = requestAnimationFrame(drawGrid);
  };
  
  drawGrid();
};

// Floating Particles
const initParticles = () => {
  const canvas = particlesCanvas.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  // Matrix-style character rain
  const matrixChars = 'ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*()_+-=[]{}|;:,.<>?';
  const fontSize = 14;
  const columns = Math.floor(canvas.width / fontSize);
  
  // Define color palettes for character rain (brighter colors)
  const colors = [
    { name: 'blue', lead: 'rgba(220, 250, 255, 1)', trail: '100, 220, 255', shadow: '#00f6ff' },
    { name: 'pink', lead: 'rgba(255, 200, 255, 1)', trail: '255, 140, 200', shadow: '#ff69b4' },
    { name: 'red', lead: 'rgba(255, 150, 150, 1)', trail: '255, 100, 100', shadow: '#ff5050' }
  ];
  
  // Create character streams (one per column)
  const streams = [];
  for (let i = 0; i < columns; i++) {
    streams.push({
      x: i * fontSize,
      y: Math.random() * canvas.height * -1, // Start above screen
      speed: Math.random() * 3 + 2, // Random fall speed
      chars: [], // Array of characters in this stream
      length: Math.floor(Math.random() * 20) + 10, // Stream length
      color: colors[Math.floor(Math.random() * colors.length)] // Random color
    });
  }
  
  const drawParticles = () => {
    // Clear canvas differently based on mode
    if (tunnelProgress.value > 0.5) {
      // Tunnel mode: Semi-transparent black to create fade trail effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    } else {
      // Normal mode: Full clear for clean background
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    streams.forEach(stream => {
      // TUNNEL MODE: Warp Speed Logic
      if (tunnelProgress.value > 0.5) {
        // Calculate angle from center
        const dx = stream.x - cx;
        const dy = stream.y - cy;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1;
        const angle = Math.atan2(dy, dx);
        
        // Speed increases with distance and gridSpeed (EXPONENTIAL)
        const speedFactor = (dist * 0.01) * (gridSpeed * 0.3);
        const moveX = Math.cos(angle) * speedFactor;
        const moveY = Math.sin(angle) * speedFactor;
        
        stream.x += moveX;
        stream.y += moveY;
        
        // Draw as stretched character stream
        const tailLength = Math.min(speedFactor * 5, 200); // Limit max stretch
        const alpha = Math.min(1, 0.5 + (gridSpeed * 0.01));
        
        // Draw the leading character (brightest)
        ctx.font = `${fontSize}px monospace`;
        ctx.fillStyle = `rgba(0, 255, 100, ${alpha})`;
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#00ff64';
        
        const char = matrixChars[Math.floor(Math.random() * matrixChars.length)];
        ctx.fillText(char, stream.x, stream.y);
        
        // Draw trail characters
        const trailSteps = Math.floor(tailLength / fontSize);
        for (let i = 1; i < trailSteps; i++) {
          const trailX = stream.x - Math.cos(angle) * (i * fontSize);
          const trailY = stream.y - Math.sin(angle) * (i * fontSize);
          const trailAlpha = alpha * (1 - i / trailSteps);
          
          ctx.fillStyle = `rgba(0, 255, 100, ${trailAlpha})`;
          ctx.shadowBlur = 10 * (1 - i / trailSteps);
          ctx.fillText(matrixChars[Math.floor(Math.random() * matrixChars.length)], trailX, trailY);
        }
        
        ctx.shadowBlur = 0;
        
        // Reset if off screen
        if (stream.x < -100 || stream.x > canvas.width + 100 || 
            stream.y < -100 || stream.y > canvas.height + 100) {
          const spawnRadius = Math.random() * 100;
          const spawnAngle = Math.random() * Math.PI * 2;
          stream.x = cx + Math.cos(spawnAngle) * spawnRadius;
          stream.y = cy + Math.sin(spawnAngle) * spawnRadius;
        }
      } 
      // NORMAL MODE: Subtle character rain background
      else {
        // Update stream position (slower than tunnel mode)
        stream.y += stream.speed * 0.4; // Much slower fall
        
        // Reset if stream goes off bottom
        if (stream.y > canvas.height + stream.length * fontSize) {
          stream.y = Math.random() * canvas.height * -1;
          stream.speed = Math.random() * 2 + 1; // Slower speed
          stream.length = Math.floor(Math.random() * 15) + 5; // Shorter streams
        }
        
        // Only draw every 2nd stream to keep it moderately dense
        if (Math.floor(stream.x / fontSize) % 2 !== 0) return;
        
        // Draw the stream in cyberpunk blue
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < stream.length; i++) {
          const charY = stream.y - (i * fontSize);
          
          // Skip if above screen
          if (charY < 0) continue;
          
          // Leading character is brightest
          if (i === 0) {
            ctx.fillStyle = stream.color.lead;
            ctx.shadowBlur = 15;
            ctx.shadowColor = stream.color.shadow;
          } else {
            // Fade from bright to dark (increased opacity)
            const alpha = (1 - (i / stream.length)) * 0.8; // Max 80% opacity (was 60%)
            ctx.fillStyle = `rgba(${stream.color.trail}, ${alpha})`;
            ctx.shadowBlur = 5 * alpha;
            ctx.shadowColor = stream.color.shadow;
          }
          
          const char = matrixChars[Math.floor(Math.random() * matrixChars.length)];
          ctx.fillText(char, stream.x, charY);
        }
        
        ctx.shadowBlur = 0;
      }
    });

    particlesAnimationId = requestAnimationFrame(drawParticles);
  };
  
  drawParticles();
};

onMounted(() => {
  // Initialize animations
  initGridAnimation();
  initParticles();
  
  // Handle window resize
  const handleResize = () => {
    if (gridCanvas.value) {
      gridCanvas.value.width = window.innerWidth;
      gridCanvas.value.height = window.innerHeight;
    }
    if (particlesCanvas.value) {
      particlesCanvas.value.width = window.innerWidth;
      particlesCanvas.value.height = window.innerHeight;
    }
  };
  window.addEventListener('resize', handleResize);
  
  // Initialize Google OAuth
  if (window.google) {
    googleClient = window.google.accounts.oauth2.initCodeClient({
      client_id: GOOGLE_CLIENT_ID,
      scope: 'email profile https://www.googleapis.com/auth/calendar',
      ux_mode: 'popup',
      callback: handleGoogleCallback,
    });
  }
});

onUnmounted(() => {
  if (gridAnimationId) cancelAnimationFrame(gridAnimationId);
  if (particlesAnimationId) cancelAnimationFrame(particlesAnimationId);
  window.removeEventListener('resize', () => {});
});

const playSound = (filename) => {
  const audio = new Audio(`/sound effect/${filename}`);
  audio.volume = 0.5;
  audio.play().catch(e => console.error("Audio play failed:", e));
};

const handleGoogleLogin = () => {
  playSound('Sci-fi UI Click.wav'); // Sound Effect
  if (googleClient) {
    googleClient.requestCode();
  } else {
    alert('Google OAuth not initialized. Please refresh the page.');
  }
};

const handleGoogleCallback = async (response) => {
  console.log("Google OAuth Response:", response);
  
  if (response.code) {
    try {
      const verifyResponse = await fetch(`${API_URL}/api/auth/google/exchange`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: response.code
        })
      });
      
      if (verifyResponse.ok) {
        const userData = await verifyResponse.json();
        console.log("User authenticated with Calendar access:", userData);
        
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('isAuthenticated', 'true');
        
        // Trigger Link Start Sequence instead of immediate push
        startLinkSequence();
      } else {
        const error = await verifyResponse.json();
        console.error("Authentication failed:", error);
        alert('Login failed. Please try again.');
      }
    } catch (error) {
      console.error("Error during authentication:", error);
      alert('Network error. Please check your connection.');
    }
  } else if (response.error) {
    console.error("OAuth error:", response.error);
    alert('Login cancelled or failed.');
  }
};

const showGuestWarning = () => {
  playSound('Sci-fi UI Click.wav'); // Sound Effect
  showWarning.value = true;
};

const proceedAsGuest = () => {
  playSound('Sci-fi UI Click.wav'); // Sound Effect
  console.log("Proceeding as guest");
  localStorage.setItem('isAuthenticated', 'guest');
  showWarning.value = false;
  // Trigger Link Start Sequence
  startLinkSequence();
};

// "Link Start" Sequence Logic
const startLinkSequence = () => {
  isLinkStart.value = true;
  linkStartPhase.value = 1; // Phase 1: Identity Verified
  linkStartText.value = "IDENTITY VERIFIED";
  playSound('Are u ready.mp3'); // Sound Effect
  
  // Sequence Timeline
  
  // T+3.0s: Initializing -> Tunnel starts forming (Delayed for audio)
  setTimeout(() => {
    linkStartPhase.value = 2;
    linkStartText.value = "CONNECTING TO VIRTUAI COMPANION...";
    playSound('lets go.mp3'); // Sound Effect
    gridSpeed = 8; 
    
    // Animate Tunnel Formation (0 to 1 over 1.5s)
    let startTime = null;
    const animateTunnel = (time) => {
        if (!startTime) startTime = time;
        const progress = (time - startTime) / 1500;
        
        if (progress < 1) {
            tunnelProgress.value = progress;
            // Slight Camera Tilt during formation
            cameraRotation.value = progress * 0.2; 
            requestAnimationFrame(animateTunnel);
        } else {
            tunnelProgress.value = 1;
        }
    };
    requestAnimationFrame(animateTunnel);
    
  }, 3000);

  // T+4.5s: Link Start (Hyperdrive Acceleration)
  setTimeout(() => {
    linkStartPhase.value = 3;
    linkStartText.value = "LINK START";
    playSound('lordsonny-long-whoosh-194554.mp3'); // Sound Effect
    
    // EXPONENTIAL ACCELERATION LOOP
    let accelStart = null;
    const accelerate = (time) => {
        if (!accelStart) accelStart = time;
        // Run this for 2.5 seconds (until whiteout)
        const duration = 2500;
        const p = Math.min(1, (time - accelStart) / duration);
        
        // Exponential Curve: Speed starts at 10, ends at 300
        // Formula: start * (base ^ p)
        // Let's try explicit frame multiplication imitation:
        // Or just map P to an exponential curve
        // speed = base + (max * p^3) -> Cubic acceleration is very strong at end
        
        const baseSpeed = 10;
        const maxSpeed = 300;
        gridSpeed = baseSpeed + (maxSpeed * Math.pow(p, 4)); // Power of 4 for extreme late acceleration
        
        // Also ramp up rotation speed
        if (p < 1) requestAnimationFrame(accelerate);
    };
    requestAnimationFrame(accelerate);
    
    // SPIRAL DIVE ANIMATION
    let spinStart = null;
    const animateSpin = (time) => {
        if (!spinStart) spinStart = time;
        const p = (time - spinStart) / 2000; // 2 seconds of spinning
        
        // Spin faster as we go
        cameraRotation.value = 0.2 + (p * Math.PI * 2); // Do a full rotation
        
        if (p < 1 && linkStartPhase.value === 3) {
            requestAnimationFrame(animateSpin);
        }
    };
    requestAnimationFrame(animateSpin);
    
  }, 4500);

  // T+6.5s: White out starts
  setTimeout(() => {
    linkStartPhase.value = 4; // White flash state
  }, 6500);

  // T+9.5s: Redirect (3 seconds of white screen)
  setTimeout(() => {
    router.push({ path: '/chat', query: { transition: 'true' } });
  }, 9500);
};
</script>

<style scoped>
/* ══════════════════════════════════════════════════════
   HIGH-TECH GLASSMORPHISM — Cyberpunk 2077 / Sci-Fi UI
   ══════════════════════════════════════════════════════ */

/* === BASE LAYER === */
.signin-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #E8EDFF;
  font-family: 'Rajdhani', sans-serif;
  position: relative;
  overflow: hidden;

  /* Multi-layered cyberpunk background:
     Layer 1 — Radial core glow (blue nexus in center)
     Layer 2 — Circuit-board micro-grid (small)
     Layer 3 — Structural macro-grid (large)
     Layer 4 — Deep navy base */
  background:
    /* Core glow */
    radial-gradient(
      ellipse 60% 50% at 50% 50%,
      rgba(0, 100, 180, 0.25) 0%,
      rgba(0, 60, 120, 0.10) 40%,
      transparent 70%
    ),
    /* Small circuit-board grid */
    linear-gradient(
      rgba(0, 180, 220, 0.07) 1px, transparent 1px
    ),
    linear-gradient(
      90deg,
      rgba(0, 180, 220, 0.07) 1px, transparent 1px
    ),
    /* Large structural grid */
    linear-gradient(
      rgba(0, 200, 255, 0.04) 1px, transparent 1px
    ),
    linear-gradient(
      90deg,
      rgba(0, 200, 255, 0.04) 1px, transparent 1px
    ),
    /* Base color */
    #000a18;
  background-size:
    100% 100%,
    20px 20px,
    20px 20px,
    80px 80px,
    80px 80px,
    100% 100%;
}

/* ══════════════════════════════════════
   PINK BORDER ANIMATION
   ══════════════════════════════════════ */
.border-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 15; /* High z-index to sit on top */
  border-radius: 12px; /* Match card border radius */
}

.border-animation span {
  position: absolute;
  display: block;
}

/* Top Border */
.border-animation span:nth-child(1) {
  top: 0;
  left: -100%;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, transparent, transparent 80%, #ff00cc 92%, #ffffff 100%);
  filter: drop-shadow(0 0 5px #ff00cc) drop-shadow(0 0 15px #ff00cc);
  animation: animate-top 8s linear infinite;
}

@keyframes animate-top {
  0% { left: -100%; }
  50%, 100% { left: 100%; }
}

/* Right Border */
.border-animation span:nth-child(2) {
  top: -100%;
  right: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, transparent, transparent 80%, #ff00cc 92%, #ffffff 100%);
  filter: drop-shadow(0 0 5px #ff00cc) drop-shadow(0 0 15px #ff00cc);
  animation: animate-right 8s linear infinite;
  animation-delay: 2s;
}

@keyframes animate-right {
  0% { top: -100%; }
  50%, 100% { top: 100%; }
}

/* Bottom Border */
.border-animation span:nth-child(3) {
  bottom: 0;
  right: -100%;
  width: 100%;
  height: 4px;
  background: linear-gradient(270deg, transparent, transparent 80%, #ff00cc 92%, #ffffff 100%);
  filter: drop-shadow(0 0 5px #ff00cc) drop-shadow(0 0 15px #ff00cc);
  animation: animate-bottom 8s linear infinite;
  animation-delay: 4s;
}

@keyframes animate-bottom {
  0% { right: -100%; }
  50%, 100% { right: 100%; }
}

/* Left Border */
.border-animation span:nth-child(4) {
  bottom: -100%;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(360deg, transparent, transparent 80%, #ff00cc 92%, #ffffff 100%);
  filter: drop-shadow(0 0 5px #ff00cc) drop-shadow(0 0 15px #ff00cc);
  animation: animate-left 8s linear infinite;
  animation-delay: 6s;
}

@keyframes animate-left {
  0% { bottom: -100%; }
  50%, 100% { bottom: 100%; }
}

/* Scanline CRT overlay — gives a monitor/HUD look */
.signin-page::before {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 200, 255, 0.015) 2px,
    rgba(0, 200, 255, 0.015) 4px
  );
  pointer-events: none;
  z-index: 3;
}

/* Code-rain / data-stream vertical tint */
.signin-page::after {
  content: '';
  position: fixed;
  inset: 0;
  background:
    /* Vertical light pillars from above */
    linear-gradient(
      180deg,
      rgba(0, 180, 255, 0.06) 0%,
      transparent 35%
    ),
    /* Subtle diagonal data-stream texture */
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 40px,
      rgba(0, 200, 255, 0.012) 40px,
      rgba(0, 200, 255, 0.012) 42px
    );
  pointer-events: none;
  z-index: 1;
}

/* === CANVAS LAYERS === */
.grid-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.particles-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  opacity: 0.7;
}

/* === VIGNETTE — deeper edges for depth === */
.vignette {
  position: fixed;
  inset: 0;
  background: radial-gradient(
    ellipse 70% 70% at 50% 50%,
    transparent 0%,
    transparent 30%,
    rgba(0, 6, 18, 0.35) 60%,
    rgba(0, 4, 12, 0.75) 85%,
    rgba(0, 2, 8, 0.95) 100%
  );
  pointer-events: none;
  z-index: 2;
}

/* === MAIN CONTAINER === */
.signin-container {
  width: 100%;
  max-width: 600px;
  padding: 2rem;
  z-index: 10;
  position: relative;
}

/* === BRAND HEADER === */
.brand-header {
  text-align: center;
  margin-bottom: 3rem;
}

.brand-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.8rem;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: 6px;
  color: #00f3ff;
  text-shadow:
    0 0 8px  rgba(0, 243, 255, 0.9),
    0 0 20px rgba(0, 243, 255, 0.6),
    0 0 40px rgba(0, 180, 255, 0.35),
    0 0 80px rgba(0, 120, 255, 0.15);
  margin: 0;
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% {
    text-shadow:
      0 0 8px  rgba(0, 243, 255, 0.9),
      0 0 20px rgba(0, 243, 255, 0.6),
      0 0 40px rgba(0, 180, 255, 0.35);
    filter: brightness(1);
  }
  50% {
    text-shadow:
      0 0 12px rgba(0, 243, 255, 1),
      0 0 30px rgba(0, 243, 255, 0.8),
      0 0 60px rgba(0, 180, 255, 0.5),
      0 0 100px rgba(0, 120, 255, 0.25);
    filter: brightness(1.15);
  }
}

.brand-subtitle {
  font-size: 0.9rem;
  color: rgba(0, 243, 255, 0.65);
  letter-spacing: 4px;
  margin-top: 1rem;
  text-transform: uppercase;
}

/* ══════════════════════════════════════
   GLASSMORPHISM CARD — Core UI Panel
   ══════════════════════════════════════ */
.signin-card {
  /* Bright ice-blue frosted glass */
  background: rgba(100, 220, 255, 0.08);
  backdrop-filter: blur(18px) brightness(1.3) saturate(150%);
  -webkit-backdrop-filter: blur(18px) brightness(1.3) saturate(150%);

  /* Cyan-glow border */
  border: 1px solid rgba(0, 220, 255, 0.35);
  border-radius: 12px;

  padding: 3rem 3.5rem;
  position: relative;

  /* Border glow */
  box-shadow:
    0 0 20px rgba(0, 200, 255, 0.15),
    0 0 50px rgba(0, 160, 255, 0.08),
    inset 0 0 40px rgba(100, 220, 255, 0.04);

  transition: all 0.4s ease;
  animation: card-border-pulse 4s ease-in-out infinite;
}

@keyframes card-border-pulse {
  0%, 100% {
    border-color: rgba(0, 220, 255, 0.30);
    box-shadow:
      0 0 20px rgba(0, 200, 255, 0.12),
      0 0 50px rgba(0, 160, 255, 0.06),
      inset 0 0 40px rgba(100, 220, 255, 0.03);
  }
  50% {
    border-color: rgba(0, 243, 255, 0.55);
    box-shadow:
      0 0 30px rgba(0, 220, 255, 0.22),
      0 0 60px rgba(0, 160, 255, 0.10),
      inset 0 0 50px rgba(100, 220, 255, 0.05);
  }
}

.signin-card:hover {
  border-color: rgba(0, 243, 255, 0.70);
  box-shadow:
    0 0 35px rgba(0, 220, 255, 0.28),
    0 0 70px rgba(0, 160, 255, 0.12),
    inset 0 0 60px rgba(100, 220, 255, 0.06);
  animation: none;
}

/* Chamfer decorations hidden — using rounded corners */
.chamfer {
  display: none;
}

/* === LOGIN OPTIONS === */
.login-options {
  margin-bottom: 2rem;
}

/* ══════════════════════════════════════════════════════
   TECH-FRAME — Chamfered Segmented Border Container
   ══════════════════════════════════════════════════════ */
.tech-frame {
  position: relative;
  width: 100%;
  padding: 2px; /* border thickness */
  /* Neon glow around the frame */
  filter: drop-shadow(0 0 6px rgba(0, 243, 255, 0.35))
          drop-shadow(0 0 15px rgba(0, 200, 255, 0.12));
  transition: filter 0.35s ease;
}

.tech-frame:hover {
  filter: drop-shadow(0 0 10px rgba(0, 243, 255, 0.55))
          drop-shadow(0 0 25px rgba(0, 200, 255, 0.20))
          drop-shadow(0 0 50px rgba(0, 160, 255, 0.10));
}

/* Top border segment — left and right halves with center gap */
.tech-frame::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* Border color */
  background: rgba(0, 243, 255, 0.7);
  /* Chamfered shape with gaps at top-center and bottom-center */
  clip-path: polygon(
    /* Top-left chamfer → gap at top center */
    0% 12px,
    12px 0%,
    calc(50% - 20px) 0%,
    calc(50% - 20px) 2px,
    12px 2px,
    2px 12px,
    2px calc(100% - 12px),
    12px calc(100% - 2px),
    calc(50% - 20px) calc(100% - 2px),
    calc(50% - 20px) 100%,
    12px 100%,
    0% calc(100% - 12px),
    0% 12px,
    /* Jump to right half — top */
    calc(50% + 20px) 0%,
    calc(100% - 12px) 0%,
    100% 12px,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    calc(50% + 20px) 100%,
    calc(50% + 20px) calc(100% - 2px),
    calc(100% - 12px) calc(100% - 2px),
    calc(100% - 2px) calc(100% - 12px),
    calc(100% - 2px) 12px,
    calc(100% - 12px) 2px,
    calc(50% + 20px) 2px,
    calc(50% + 20px) 0%
  );
  pointer-events: none;
  z-index: 1;
  transition: background 0.35s ease;
}

.tech-frame:hover::before {
  background: rgba(0, 243, 255, 0.9);
}

/* Google Button — transparent with chamfered clip */
.btn-google {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.06);
  color: #e8edff;
  border: none;
  padding: 16px 24px;
  font-family: 'Roboto', sans-serif;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2; /* Force above background elements */

  /* Chamfered shape matching the frame */
  clip-path: polygon(
    12px 0%, calc(100% - 12px) 0%,
    100% 12px, 100% calc(100% - 12px),
    calc(100% - 12px) 100%, 12px 100%,
    0% calc(100% - 12px), 0% 12px
  );
}

.btn-google:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.btn-google:active {
  background: rgba(255, 255, 255, 0.18);
}

.google-icon {
  flex-shrink: 0;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  margin: 2rem 0;
  color: rgba(0, 220, 255, 0.5);
  font-size: 0.75rem;
  letter-spacing: 4px;
  font-weight: 600;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    rgba(0, 220, 255, 0.35),
    transparent
  );
}

.divider span {
  padding: 0 1.5rem;
}

/* ══════════════════════════════════════
   GHOST BUTTON — Neon Chamfered Style
   ══════════════════════════════════════ */
.btn-guest {
  width: 100%;
  background: transparent;
  border: none;
  color: #00f3ff;
  padding: 16px 24px;
  cursor: pointer;
  font-family: 'Orbitron', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 3px;
  transition: all 0.35s ease;
  text-transform: uppercase;
  position: relative;

  /* Chamfered shape matching the frame */
  clip-path: polygon(
    12px 0%, calc(100% - 12px) 0%,
    100% 12px, 100% calc(100% - 12px),
    calc(100% - 12px) 100%, 12px 100%,
    0% calc(100% - 12px), 0% 12px
  );
}

.btn-guest:hover {
  background: rgba(0, 243, 255, 0.10);
  color: #ffffff;
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.8);
}

.btn-guest:active {
  background: rgba(0, 243, 255, 0.20);
}

/* === TERMS === */
.terms {
  font-size: 0.75rem;
  color: rgba(120, 160, 200, 0.5);
  margin-top: 2rem;
  margin-bottom: 1rem;
  text-align: center;
  letter-spacing: 0.5px;
}

/* === BACK LINK === */
.back-link {
  text-align: center;
  margin-top: 1.5rem;
}

.back-link a {
  color: rgba(0, 220, 255, 0.55);
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.back-link a:hover {
  color: #00f3ff;
  text-shadow: 0 0 12px rgba(0, 243, 255, 0.6);
}

/* ══════════════════════════════════════
   MODAL — Warning Panel
   ══════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 4, 12, 0.92);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(0, 10, 24, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 243, 255, 0.4);
  padding: 2.5rem;
  border-radius: 12px;
  max-width: 420px;
  width: 90%;
  box-shadow:
    0 0 30px rgba(0, 200, 255, 0.20),
    0 20px 60px rgba(0, 0, 0, 0.65);
}

.modal-header h3 {
  font-family: 'Orbitron', sans-serif;
  color: #00f3ff;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  text-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
  letter-spacing: 2px;
}

.warning-text {
  color: rgba(232, 237, 255, 0.85);
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.restriction-list {
  text-align: left;
  margin: 1.5rem 0 2rem 1.5rem;
  color: rgba(200, 215, 235, 0.65);
  font-size: 0.9rem;
  line-height: 1.8;
}

.restriction-list li {
  margin-bottom: 0.7rem;
}

.restriction-list li::marker {
  color: rgba(0, 243, 255, 0.5);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-confirm {
  background: rgba(0, 243, 255, 0.12);
  border: 1.5px solid rgba(0, 243, 255, 0.7);
  color: #00f3ff;
  padding: 0.8rem 1.8rem;
  border-radius: 3px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
}

.btn-confirm:hover {
  background: rgba(0, 243, 255, 0.25);
  box-shadow:
    0 0 20px rgba(0, 243, 255, 0.45),
    0 0 50px rgba(0, 200, 255, 0.15),
    inset 0 0 15px rgba(0, 243, 255, 0.10);
}

.btn-cancel {
  background: transparent;
  border: 1.5px solid rgba(0, 220, 255, 0.25);
  color: rgba(0, 220, 255, 0.6);
  padding: 0.8rem 1.8rem;
  border-radius: 3px;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  text-transform: uppercase;
}

.btn-cancel:hover {
  border-color: rgba(0, 243, 255, 0.5);
  color: rgba(0, 243, 255, 0.8);
  background: rgba(0, 220, 255, 0.05);
}

/* ══════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════ */
@media (max-width: 768px) {
  .signin-container {
    max-width: 500px;
    padding: 1.5rem;
  }

  .brand-title {
    font-size: 2.4rem;
    letter-spacing: 5px;
  }

  .signin-card {
    padding: 2.5rem 2rem;
  }
}

@media (max-width: 480px) {
  .signin-container {
    max-width: 100%;
    padding: 1rem;
  }

  .brand-title {
    font-size: 2rem;
    letter-spacing: 3px;
  }

  .signin-card {
    padding: 2rem 1.5rem;
  }

  .modal-content {
    padding: 2rem 1.5rem;
  }

  .btn-guest {
    letter-spacing: 2px;
    font-size: 12px;
  }
}
/* ══════════════════════════════════════
   LINK START ANIMATION STYLES
   ══════════════════════════════════════ */
.link-start-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 20;
  height: 100vh;
  width: 100vw;
  perspective: 1000px;
}

.link-content {
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

.verified-badge {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #00f3ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
  animation: pulse-badge 1s infinite;
}

.check-icon {
  font-size: 40px;
  color: #00f3ff;
}

.link-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5rem;
  color: #E8EDFF;
  letter-spacing: 5px;
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.8);
  margin-bottom: 2rem;
}

.loading-bar-container {
  width: 300px;
  height: 4px;
  background: rgba(0, 243, 255, 0.2);
  margin: 0 auto;
  border-radius: 2px;
  overflow: hidden;
}

.loading-bar {
  height: 100%;
  background: #00f3ff;
  width: 0%;
  animation: fillBar 1.5s ease-in-out forwards;
  box-shadow: 0 0 10px #00f3ff;
}

@keyframes fillBar {
  0% { width: 0%; }
  100% { width: 100%; }
}

@keyframes pulse-badge {
  0% { transform: scale(1); box-shadow: 0 0 20px rgba(0, 243, 255, 0.5); }
  50% { transform: scale(1.1); box-shadow: 0 0 40px rgba(0, 243, 255, 0.8); }
  100% { transform: scale(1); box-shadow: 0 0 20px rgba(0, 243, 255, 0.5); }
}

/* Rings */
/* Rings Removed */

.glitch-text {
  animation: glitch-anim 0.1s infinite;
  color: #fff;
  font-size: 5rem;
  letter-spacing: 15px;
  text-shadow: 0 0 20px #00f3ff, 0 0 40px #00f3ff;
}

@keyframes glitch-anim {
  0% { transform: translate(0) }
  20% { transform: translate(-5px, 5px) }
  40% { transform: translate(-5px, -5px) }
  60% { transform: translate(5px, 5px) }
  80% { transform: translate(5px, -5px) }
  100% { transform: translate(0) }
}



/* White Flash */
.white-flash {
  position: fixed;
  inset: 0;
  background: white;
  opacity: 0;
  pointer-events: none;
  z-index: 100;
  transition: opacity 0.5s ease;
}

.white-flash.active {
  opacity: 1;
}
</style>


