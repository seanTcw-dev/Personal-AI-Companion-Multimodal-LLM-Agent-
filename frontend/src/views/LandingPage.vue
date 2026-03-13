<template>
  <div class="landing-page">
    <!-- Animated 3D Grid Floor -->
    <canvas ref="gridCanvas" class="grid-canvas"></canvas>
    
    <!-- Floating Particles -->
    <canvas ref="particlesCanvas" class="particles-canvas"></canvas>
    
    <!-- Vignette Overlay -->
    <div class="vignette"></div>
    <div class="fog-layer"></div>
    
    <!-- Vignette Overlay -->
    <div class="vignette"></div>
    <div class="fog-layer"></div>
    
    <header class="landing-header">
      <div class="logo">
        <div class="logo-ring">
          <span class="logo-v">V</span>
        </div>
        <span>VirtuA<span class="serif-i">I</span> Companion</span>
      </div>
      <nav>
        <router-link to="/login" class="btn-tron-primary" @click="playSound('Sci-fi UI Click.wav')">
          <span class="btn-text">INITIALIZE SYSTEM</span>
          <span class="btn-glitch"></span>
        </router-link>
      </nav>
    </header>

    <main class="hero-section">
      <div class="hero-content">
        <h1 class="glitch-title" data-text="WELCOME TO VIRTUAI COMPANION">WELCOME TO VIRTUAI COMPANION</h1>
        <p class="hero-subtitle">Experience the next generation of digital interaction.</p>
        
        <div class="feature-grid">
          <!-- Feature 1 -->
          <div class="tech-frame feature-frame">
            <div class="feature-card-content">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                  <circle cx="12" cy="5" r="2"></circle>
                  <path d="M12 7v4"></path>
                  <line x1="8" y1="16" x2="8" y2="16"></line>
                  <line x1="16" y1="16" x2="16" y2="16"></line>
                </svg>
              </div>
              <h3>INTELLIGENT AI</h3>
              <p>ADVANCED NEURAL NETWORKS PROCESSING NATURAL LANGUAGE IN REAL-TIME.</p>
            </div>
          </div>
          
          <!-- Feature 2 -->
          <div class="tech-frame feature-frame">
            <div class="feature-card-content">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
              </div>
              <h3>VOICE SYNTHESIS</h3>
              <p>HIGH-FIDELITY AUDIO GENERATION WITH EMOTIONAL RESONANCE.</p>
            </div>
          </div>

          <!-- Feature 3 -->
          <div class="tech-frame feature-frame">
            <div class="feature-card-content">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </div>
              <h3>VISUAL RECOGNITION</h3>
              <p>REAL-TIME EMOTION ANALYSIS AND VISUAL CONTEXT UNDERSTANDING.</p>
            </div>
          </div>
        </div>

        <div class="cta-container">
          <router-link to="/login" class="btn-tron-large" @click="playSound('Sci-fi UI Click.wav')">
            ENTER THE SYSTEM
            <div class="btn-scanline"></div>
          </router-link>
        </div>
      </div>
    </main>

    <footer class="landing-footer">
      <p>SYSTEM.VERSION.2.0.24 // VIRTUAI.CORP // ALL.RIGHTS.RESERVED</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const gridCanvas = ref(null);
const particlesCanvas = ref(null);

const playSound = (filename) => {
  const audio = new Audio(`/sound effect/${filename}`);
  audio.volume = 0.5;
  audio.play().catch(e => console.error("Audio play failed:", e));
};

let gridAnimationId = null;
let particlesAnimationId = null;

// Animated 3D Grid Floor logic (ported and adapted)
const initGridAnimation = () => {
  const canvas = gridCanvas.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  let offset = 0;
  let skyRotation = 0;
  const gridSize = 25; // Smaller grid size for density 
  
  const drawGrid = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const centerX = canvas.width / 2;
    const horizonY = canvas.height * 0.45;

    // --- 1. SKY & RINGS ---
    // Draw slowly rotating sky rings
    ctx.save();
    ctx.translate(centerX, horizonY - 100);
    ctx.rotate(skyRotation);
    
    for (let i = 1; i <= 3; i++) {
        ctx.beginPath();
        ctx.arc(0, 0, canvas.width * (0.3 + i * 0.15), 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0, 243, 255, ${0.05 - i * 0.01})`;
        ctx.lineWidth = 20 + i * 10; // thick bands
        ctx.stroke();
        
        // Thin glowing line inside
        ctx.beginPath();
        ctx.arc(0, 0, canvas.width * (0.3 + i * 0.15), 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0, 243, 255, ${0.15})`;
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    ctx.restore();
    skyRotation += 0.0002;

    // --- 2. DISTANT CITY SKYLINE ---
    // Draw simple glowing blocks on the horizon
    const cityCount = 40;
    const cityWidth = canvas.width / cityCount;
    for (let i = 0; i < cityCount; i++) {
        const height = Math.sin(i * 132.5) * 50 + Math.cos(i * 43.2) * 80 + 100; // Deterministic random height
        const x = i * cityWidth;
        // Fade gradient for buildings
        const bGrad = ctx.createLinearGradient(0, horizonY - height, 0, horizonY);
        bGrad.addColorStop(0, 'rgba(0, 243, 255, 0)');
        bGrad.addColorStop(1, `rgba(0, 243, 255, ${0.1 + Math.sin(i)*0.05})`);
        
        ctx.fillStyle = bGrad;
        ctx.fillRect(x, horizonY - height, cityWidth * 0.8, height);
    }
    
    // Tron Blue/Cyan Gradient for floor
    const gradient = ctx.createLinearGradient(0, horizonY, 0, canvas.height);
    gradient.addColorStop(0, 'rgba(0, 243, 255, 0)');
    gradient.addColorStop(0.2, 'rgba(0, 243, 255, 0.1)'); 
    gradient.addColorStop(1, 'rgba(0, 243, 255, 0.4)'); 
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 1;
    
    // --- 3. HORIZONTAL GRID LINES (Infinite Perspective) ---
    // Use exponential distribution for density at horizon
    const totalLines = 20;
    const speed = (offset / gridSize); // 0 to 1
    
    for (let i = 0; i < totalLines; i++) {
        // Calculate relative position (0 at horizon, 1 at bottom)
        // We add the speed offset to simulate movement
        let relY = (i + speed) / totalLines;
        
        // Wrap around
        if (relY > 1) relY -= 1;
        
        // Apply exponential curve for perspective (y = x^3 to bunch up at horizon)
        // 0 input -> 0 output (horizon)
        // 1 input -> 1 output (bottom)
        const curve = Math.pow(relY, 3);
        
        const y = horizonY + curve * (canvas.height - horizonY);
        
        // Styles based on depth
        // Near horizon (curve close to 0): Thin, spaced, bright? No, classic grid is dense at horizon.
        // Actually, lines merge at horizon. 
        // Brightness: Fade out at very bottom (too close) or very top (horizon)
        
        const alpha = Math.min(1, curve * 1.5) * (1 - Math.pow(curve, 5)); // Fade at horizon and slightly at bottom
        
        // Width increases with proximity
        const lineWidth = 1 + curve * 3; 
        
        const width = canvas.width * (0.2 + curve * 1.5); // Wider as it gets closer
        const x = centerX - width / 2;
        
        ctx.globalAlpha = alpha;
        ctx.lineWidth = lineWidth;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + width, y);
        ctx.stroke();

        // Ground Circuits (occasional glowing pulses)
        if (i % 3 === 0 && curve > 0.1) {
            ctx.save();
            ctx.strokeStyle = `rgba(0, 243, 255, ${0.3 * alpha})`;
            ctx.lineWidth = lineWidth * 2;
            ctx.shadowBlur = 10 * curve;
            ctx.shadowColor = '#00f3ff';
            ctx.beginPath();
            // Partial lines for 'circuit' feel
            const segWidth = width * 0.1;
            const segX = x + width * 0.2 + (i % 5) * segWidth;
            ctx.moveTo(segX, y);
            ctx.lineTo(segX + segWidth, y);
            ctx.stroke();
            ctx.restore();
        }
    }
    
    // --- 4. VERTICAL GRID LINES ---
    for (let i = -20; i <= 20; i++) {
      // Fade verticals near horizon
      const grad = ctx.createLinearGradient(0, horizonY, 0, canvas.height);
      grad.addColorStop(0, 'rgba(0, 243, 255, 0)');
      grad.addColorStop(0.2, 'rgba(0, 243, 255, 0.2)');
      grad.addColorStop(1, 'rgba(0, 243, 255, 0.1)');
      
      ctx.strokeStyle = grad;
      ctx.lineWidth = 1 + Math.abs(i) * 0.05; // Slightly thicker outer lines?
      ctx.beginPath();
      
      const startX = centerX + (i * gridSize * 0.5); // Tighter at horizon
      const endX = centerX + (i * gridSize * 12);   // Fanned out wide
      
      ctx.moveTo(startX, horizonY);
      ctx.lineTo(endX, canvas.height);
      ctx.stroke();
    }
    
    // --- 5. SIDE WALLS (TUNNEL EFFECT) ---
    // Walls are vertical planes at left and right extremes
    
    const drawWall = (isLeft) => {
        const wallX = isLeft ? 0 : canvas.width;
        const lookDir = isLeft ? 1 : -1;
        
        ctx.save();
        
        // Gradient for the wall (Fade out towards center)
        const wallGrad = ctx.createLinearGradient(
            isLeft ? 0 : canvas.width, 
            0, 
            isLeft ? canvas.width * 0.3 : canvas.width * 0.7, 
            0
        );
        wallGrad.addColorStop(0, 'rgba(0, 243, 255, 0.4)');
        wallGrad.addColorStop(1, 'rgba(0, 243, 255, 0)');
        
        // Clip to side regions
        ctx.beginPath();
        if (isLeft) {
            ctx.rect(0, 0, canvas.width * 0.25, canvas.height);
        } else {
            ctx.rect(canvas.width * 0.75, 0, canvas.width * 0.25, canvas.height);
        }
        ctx.clip();
        
        // Perspective Horizontal Lines (Moving towards viewer)
        // They should match the floor lines in Z-space theoretically, but visuals matter more.
        // We'll use the same 'offset' logic adapted for vertical spacing on walls? 
        // No, purely horizontal lines on walls appear to radiate from vanishing point.
        // WAIT. "Lines on floor move towards viewer". On walls, horizontal lines also move towards viewer.
        // Visually, these are lines radiating from the Horizon Y, fanning out up and down.
        // NO, those are the "horizontal" physical lines.
        // The "Vertical" physical columns appear as vertical lines moving side-to-side?
        
        // LET'S SIMPLIFY:
        // 1. Longitudinal lines (going into distance): Radiate from (centerX, horizonY) outwards.
        // 2. Latitudinal lines (moving towards cam): Expand from center?
        
        // Drawing "longitudinal" lines (The ones that create the tunnel depth)
        // These radiate from the vanishing point (centerX, horizonY)
        const rays = 12;
        ctx.strokeStyle = wallGrad;
        ctx.lineWidth = 1;
        
        for (let i = 0; i < rays; i++) {
            // Angle spread for the wall
            const baseAngle = isLeft ? Math.PI : 0; // Left or Right
            const spread = (Math.PI / 1.5) * (i / rays) - (Math.PI / 3); 
            // This logic is tricky. Let's just draw lines from Horizon to Edge.
            
            const destY = (i / rays) * canvas.height;
            const destX = isLeft ? 0 : canvas.width;
            
            ctx.beginPath();
            ctx.moveTo(centerX, horizonY);
            ctx.lineTo(destX, destY);
            ctx.stroke();
        }

        // Drawing "latitudinal" lines (The ribs of the tunnel moving forward)
        // These are vertical-ish arcs or straight lines that scale up.
        // For a box tunnel, they are simple vertical lines that move outwards from center X.
        
        const numRibs = 15;
        for(let i=0; i<numRibs; i++) {
             // Use similar exp logic to floor Z
             let relZ = (i + (offset/gridSize)) / numRibs;
             if (relZ > 1) relZ -= 1;
             
             // 0 = horizon, 1 = viewer
             const depth = Math.pow(relZ, 3);
             
             // X position expands from center
             // Left wall: starts at centerX, moves to 0
             // Right wall: starts at centerX, moves to width
             
             let xPos;
             if (isLeft) {
                 xPos = centerX - (centerX * depth * 1.5); // 1.5 multiplier to push it off screen fast
             } else {
                 xPos = centerX + ((canvas.width - centerX) * depth * 1.5);
             }
             
             // Draw vertical-ish rib
             ctx.strokeStyle = `rgba(0, 243, 255, ${0.4 * (1-depth)})`; // Bright at horizon, dim at viewer? Or opposite? 
             // "Bright at far edges, fade to transparent at center" -> user said.
             // XPos determines nreness to center.
             
             const distFromCenter = Math.abs(xPos - centerX);
             const opacity = Math.min(1, Math.pow(distFromCenter / (canvas.width/3), 2));
             
             ctx.strokeStyle = `rgba(0, 243, 255, ${opacity * 0.5})`;
             ctx.lineWidth = 2;
             
             ctx.beginPath();
             ctx.moveTo(xPos, 0);
             ctx.lineTo(xPos, canvas.height);
             ctx.stroke();
             
             // HUD DETAILS: Ruler markings / Binary
             if (depth > 0.2 && depth < 0.9 && i % 2 === 0) {
                 ctx.fillStyle = `rgba(0, 243, 255, ${opacity})`;
                 ctx.font = '10px monospace';
                 const textX = isLeft ? xPos + 5 : xPos - 15;
                 
                 // Ruler ticks
                 for(let t=0; t<10; t++) {
                     const tickY = canvas.height * 0.2 + t * 50;
                     ctx.fillRect(isLeft ? xPos : xPos-4, tickY, 4, 1);
                 }
                 
                 // Random Binary (Reduced flickering)
                 if (Math.random() > 0.995) {
                    const bin = Math.random().toString(2).substr(2, 4);
                    ctx.fillText(bin, textX, canvas.height/2 + i*20);
                 }
             }
        }

        ctx.restore();
    };

    drawWall(true);  // Left Wall
    drawWall(false); // Right Wall
    
    // Animate (Slower speed)
    offset += 0.15; // Constant speed unit
    if (offset > gridSize) offset = 0; // Loop logic handled in math above instead
    
    gridAnimationId = requestAnimationFrame(drawGrid);
  };
  
  drawGrid();
};

const initParticles = () => {
  const canvas = particlesCanvas.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  const particles = [];
  const particleCount = 40;
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      size: Math.random() * 2,
      opacity: Math.random() * 0.5 + 0.1
    });
  }
  
  const drawParticles = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;
      
      ctx.fillStyle = `rgba(0, 243, 255, ${p.opacity})`;
      ctx.shadowBlur = 5;
      ctx.shadowColor = '#00f3ff';
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });
    
    particlesAnimationId = requestAnimationFrame(drawParticles);
  };
  
  drawParticles();
};

onMounted(() => {
  initGridAnimation();
  initParticles();
  
  window.addEventListener('resize', () => {
    if (gridCanvas.value) {
      gridCanvas.value.width = window.innerWidth;
      gridCanvas.value.height = window.innerHeight;
    }
    if (particlesCanvas.value) {
      particlesCanvas.value.width = window.innerWidth;
      particlesCanvas.value.height = window.innerHeight;
    }
  });
});

onUnmounted(() => {
  if (gridAnimationId) cancelAnimationFrame(gridAnimationId);
  if (particlesAnimationId) cancelAnimationFrame(particlesAnimationId);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

/* === TRON THEME VARIABLES === */
:root {
  --tron-cyan: #00f3ff;
  --tron-cyan-dim: rgba(0, 243, 255, 0.4);
  --tron-dark: #020204;
  --tron-panel: rgba(2, 10, 20, 0.85);
}

.landing-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: #E8EDFF;
  font-family: 'Rajdhani', sans-serif;
  position: relative;
  overflow: hidden;

  /* Multi-layered cyberpunk background from Login Page */
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

/* Scanline CRT overlay */
.landing-page::before {
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

/* === BACKGROUND LAYERS === */
.grid-canvas, .particles-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.grid-canvas { z-index: 0; opacity: 0.4; }
.particles-canvas { z-index: 1; opacity: 0.6; }

.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, transparent 40%, rgba(0, 10, 24, 0.8) 95%);
  pointer-events: none;
  z-index: 2;
}

.fog-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 60%;
  background: linear-gradient(to bottom, 
      rgba(0, 243, 255, 0.02) 0%, 
      rgba(0, 243, 255, 0.1) 80%, 
      rgba(0, 0, 0, 0) 100%);
  filter: blur(20px);
  pointer-events: none;
  z-index: 1;
}

/* Side Grids */
/* Removed CSS side-lines in favor of Canvas implementation */

/* === HEADER === */
.landing-header {
  position: relative;
  z-index: 10;
  padding: 1.5rem 3rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 243, 255, 0.15);
  background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Orbitron', sans-serif;
  color: #00f3ff;
  letter-spacing: 2px;
  font-size: 1.2rem;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
}

.serif-i {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-style: normal;
}

.logo-ring {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00f3ff, #ff00ff);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    -2px -2px 10px rgba(0, 243, 255, 0.4),
    2px 2px 10px rgba(255, 0, 255, 0.4);
}

.logo-ring::before {
  content: '';
  position: absolute;
  top: 3.5px; left: 3.5px; right: 3.5px; bottom: 3.5px;
  background-color: #000a18;
  border-radius: 50%;
  z-index: 1;
}

.logo-v {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8rem;
  font-weight: 900;
  color: #fff;
  text-shadow: 
    0 0 8px rgba(255, 255, 255, 0.8);
  position: relative;
  z-index: 1;  padding-left: 1px;
  margin-top: 3.5px;}

@keyframes hud-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes hud-spin-reverse {
  0% { transform: rotate(360deg); }
  100% { transform: rotate(0deg); }
}

/* === HERO SECTION === */
.hero-section {
  flex: 1;
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding-bottom: 5vh; /* Lift content slightly */
}

.hero-content {
  max-width: 1200px;
  padding: 2rem;
}

.glitch-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 4.5rem;
  font-weight: 900;
  letter-spacing: 8px;
  margin: 0;
  color: #fff;
  text-shadow: 
    0 0 10px rgba(0, 243, 255, 0.8),
    0 0 20px rgba(0, 243, 255, 0.4);
  position: relative;
}

/* Simple glitch effect using before/after */
.glitch-title::before,
.glitch-title::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.glitch-title::before {
  left: 2px;
  text-shadow: -1px 0 #ff00cc;
  clip: rect(44px, 450px, 56px, 0);
  animation: glitch-anim 5s infinite linear alternate-reverse;
}

.glitch-title::after {
  left: -2px;
  text-shadow: -1px 0 #00f3ff;
  clip: rect(44px, 450px, 56px, 0);
  animation: glitch-anim2 5s infinite linear alternate-reverse;
}

@keyframes glitch-anim {
  0% { clip: rect(42px, 9999px, 44px, 0); }
  5% { clip: rect(12px, 9999px, 54px, 0); }
  10% { clip: rect(82px, 9999px, 12px, 0); }
  100% { clip: rect(22px, 9999px, 64px, 0); }
}

@keyframes glitch-anim2 {
  0% { clip: rect(12px, 9999px, 84px, 0); }
  5% { clip: rect(92px, 9999px, 14px, 0); }
  100% { clip: rect(2px, 9999px, 94px, 0); }
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(232, 237, 255, 0.7);
  letter-spacing: 3px;
  margin-top: 1rem;
  margin-bottom: 2.5rem; /* Reduced from 4rem */
  text-transform: uppercase;
}

/* === FEATURE GRID (HUD CARDS) === */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-bottom: 1.5rem; /* Reduced margin further */
}

/* === TECH FRAME (Chamfered Border) === */
.tech-frame {
  position: relative;
  width: 100%;
  padding: 2px; /* Border thickness */
  filter: drop-shadow(0 0 6px rgba(0, 243, 255, 0.35))
          drop-shadow(0 0 15px rgba(0, 200, 255, 0.12));
  transition: filter 0.35s ease;
}

.tech-frame:hover {
  filter: drop-shadow(0 0 10px rgba(0, 243, 255, 0.55))
          drop-shadow(0 0 25px rgba(0, 200, 255, 0.20))
          drop-shadow(0 0 50px rgba(0, 160, 255, 0.10));
}

.tech-frame::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 243, 255, 0.7);
  /* Chamfered shape with gaps at top-center and bottom-center (Copied from SignInPage) */
  clip-path: polygon(
    0% 12px, 12px 0%, calc(50% - 20px) 0%, calc(50% - 20px) 2px, 12px 2px, 2px 12px, 2px calc(100% - 12px), 12px calc(100% - 2px), calc(50% - 20px) calc(100% - 2px), calc(50% - 20px) 100%, 12px 100%, 0% calc(100% - 12px), 0% 12px,
    calc(50% + 20px) 0%, calc(100% - 12px) 0%, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, calc(50% + 20px) 100%, calc(50% + 20px) calc(100% - 2px), calc(100% - 12px) calc(100% - 2px), calc(100% - 2px) calc(100% - 12px), calc(100% - 2px) 12px, calc(100% - 12px) 2px, calc(50% + 20px) 2px, calc(50% + 20px) 0%
  );
  pointer-events: none;
  z-index: 1;
  transition: background 0.35s ease;
}

.tech-frame:hover::before {
  background: rgba(0, 243, 255, 0.9);
}

/* === FEATURE CARD CONTENT (Inner) === */
.feature-card-content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(100, 220, 255, 0.08); /* Ice blue tint */
  padding: 2.5rem 1.5rem;
  
  /* Chamfered clip for content */
  clip-path: polygon(
    12px 0%, calc(100% - 12px) 0%,
    100% 12px, 100% calc(100% - 12px),
    calc(100% - 12px) 100%, 12px 100%,
    0% calc(100% - 12px), 0% 12px
  );
  
  transition: all 0.3s ease;
}

.feature-frame:hover .feature-card-content {
  background: rgba(100, 220, 255, 0.12);
}

/* Cleaned up old styles */

/* Feature Icon & Text - Minor adjustments for new layout if needed */
.feature-icon {
  margin-bottom: 1.5rem;
  width: 56px;
  height: 56px;
  color: #00f3ff;
  filter: drop-shadow(0 0 5px rgba(0, 243, 255, 0.5));
}

/* Feature Text Styling */
.feature-card-content h3 {
  font-family: 'Orbitron', sans-serif;
  color: #E8EDFF;
  margin: 0.5rem 0;
  font-size: 1.2rem;
  letter-spacing: 2px;
  text-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
}

.feature-frame:hover .feature-card-content h3 {
  color: #00f3ff;
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.8);
}

.feature-card-content p {
  font-size: 0.9rem;
  color: #8fa0b5;
  line-height: 1.6;
  font-family: 'Rajdhani', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 600;
  margin-top: 0.5rem;
  max-width: 250px;
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 1.5rem auto; /* Center the icon */
  color: #00f3ff;
  filter: drop-shadow(0 0 8px rgba(0, 243, 255, 0.6));
  display: flex;
  justify-content: center;
  align-items: center;
}

.feature-icon svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* Card Corners */
/* Card Corners - Removed (replaced by Tech Frame) */

/* === BUTTONS === */
.btn-tron-primary, .btn-tron-large {
  position: relative;
  text-decoration: none;
  font-family: 'Orbitron', sans-serif;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-tron-primary {
  padding: 10px 24px;
  font-size: 0.9rem;
  color: var(--tron-cyan, #00f3ff);
  border: 1px solid rgba(0, 243, 255, 0.3);
  letter-spacing: 1px;
}

.btn-tron-primary:hover {
  background: rgba(0, 243, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
  border-color: rgba(0, 243, 255, 0.8);
}

.btn-tron-large {
  padding: 1.2rem 3.5rem;
  font-size: 1.4rem;
  font-weight: 700;
  color: #020204;
  background: var(--tron-cyan, #00f3ff);
  letter-spacing: 3px;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.4);
  clip-path: polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px);
}

.btn-tron-large:hover {
  background: #fff;
  color: #000;
  box-shadow: 0 0 40px rgba(0, 243, 255, 0.7);
}

/* === FOOTER === */
.landing-footer {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 1.5rem;
  color: rgba(0, 243, 255, 0.3);
  font-size: 0.8rem;
  letter-spacing: 2px;
  border-top: 1px solid rgba(0, 243, 255, 0.1);
}

@media (max-width: 768px) {
  .hero-content { padding: 1rem; }
  .glitch-title { font-size: 2.5rem; }
  .feature-grid { grid-template-columns: 1fr; }
  .landing-header { padding: 1rem; }
}
</style>
