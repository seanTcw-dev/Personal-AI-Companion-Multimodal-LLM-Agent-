# 🎭 VRM Model Viewer - Quick Start

## ✅ What This Does

A simple, standalone VRM model viewer with interactive controls. Uses the **exact same approach** as your main frontend project.

## 🚀 How to Run

### Option 1: Using the existing server script
```powershell
cd "c:\Users\SeanTeng\Desktop\Anime Model Chatbot v3\3dModeltest"
.\start.ps1
```

Then open: **http://localhost:8000/viewer.html**

### Option 2: Start server manually
```powershell
cd "c:\Users\SeanTeng\Desktop\Anime Model Chatbot v3\3dModeltest"
npx http-server -p 8000
```

Then open: **http://localhost:8000/viewer.html**

## 🎮 Controls

### **Mouse Controls:**
- **Left Click + Drag** → Rotate camera around model
- **Right Click + Drag** → Pan camera
- **Scroll Wheel** → Zoom in/out

### **Expression Controls:**
1. Select expression from dropdown (Happy, Sad, Angry, etc.)
2. Adjust intensity slider (0.0 to 1.0)
3. See changes in real-time!
4. Click "Reset Expression" to return to neutral

## 🎨 Features

✅ **Same as Your Frontend:**
- Three-point lighting (key, fill, rim, front)
- Character wrapper with scale 2.1x
- Arms relaxed from T-pose
- Position adjusted to -0.6 Y
- VRMUtils.rotateVRM0 applied

✅ **Additional Features:**
- OrbitControls for mouse interaction
- Live expression testing
- Intensity slider for fine control
- Visual feedback and console logs

## 📂 Files

- `viewer.html` - VRM model viewer (this file)
- `avatar.vrm` - Your VRM model
- `start.ps1` - Server startup script

## 🎯 What You'll See

When you open the viewer:
1. **Loading screen** with cyberpunk style
2. **3D model** appears in center
3. **Control panel** (top-left) for expressions
4. **Info panel** (bottom-left) with instructions
5. **Interactive camera** - drag to rotate!

## 🔧 Technical Details

### **Matching Your Frontend:**

| Feature | Implementation |
|---------|---------------|
| **Camera** | FOV 30°, position (0, 3.0, 6.5) |
| **Scaling** | 2.1x via wrapper group |
| **Position** | Y = -0.6 |
| **Lighting** | 4-light setup (key, fill, rim, front) |
| **T-pose fix** | Arms rotated (±0.8, ±0.3) |
| **Rotation** | VRMUtils.rotateVRM0 |

### **New Features:**

- **OrbitControls** - Mouse camera control
- **Expression UI** - Dropdown + slider
- **Real-time updates** - Instant feedback

## 🧪 Testing Expressions

Available expressions to test:
- `neutral` - Default calm face
- `happy` - Smiling
- `sad` - Sad face
- `angry` - Angry expression
- `surprised` - Wide-eyed surprise
- `relaxed` - Calm, peaceful
- `joy` - Very happy
- `sorrow` - Deep sadness
- `fun` - Playful
- `blink` - Eyes closed
- `blinkLeft` - Left eye closed
- `blinkRight` - Right eye closed

## 💡 Use Cases

**Perfect for:**
- 🎨 Testing expressions before coding
- 🔍 Exploring model capabilities
- 🎮 Understanding bone structure
- 📸 Taking screenshots
- 🧪 Experimenting with lighting
- 📐 Checking model scale/position

## 🐛 Troubleshooting

### "Failed to load VRM model"
- Make sure `avatar.vrm` is in the same folder as `viewer.html`
- Check console for specific errors
- Verify server is running (should see files at http://localhost:8000)

### "Expression not working"
- Not all models have all expressions
- Check console for warnings
- Some expressions might have different names

### "Model looks wrong"
- This viewer uses **exact same settings** as your frontend
- If it looks different, compare lighting/camera values
- Check console logs for setup details

## 🎉 Next Steps

Once you're happy with the viewer:
1. Use it as reference for your main app
2. Test new expressions here first
3. Experiment with camera angles
4. Check model quality and details

---

**Now you have a dedicated VRM testing environment!** 🚀

Open http://localhost:8000/viewer.html and start experimenting!
