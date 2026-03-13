# 🎭 VRM Model Inspector - Quick Start

Simple HTML tool to inspect VRM model components (bones, expressions, materials, meshes).

## ⚡ Quick Start (Recommended)

Just run this command:
```powershell
.\start.ps1
```

This will:
- Start a local web server on port 8000
- Auto-open your browser to http://localhost:8000/index.html
- No installation needed (uses npx)

## 🔍 How to Use

1. Click the **"Inspect Model"** button
2. The tool will analyze `avatar.vrm` and show:
   - 📊 Basic info (name, author, version)
   - 😊 All available expressions
   - 🦴 All bones you can control
   - 🎨 Materials used
   - 🔺 Mesh complexity (vertices, faces)
3. A formatted `.txt` report will **auto-download** with all the details!

## 📥 Output

You'll get a file like:
```
VRM-Model-Components-AvatarSample_A-1759919673082.txt
```

This contains all the expressions and bones you can use in your code!

## 🔧 Alternative Ways to Start

### Option 1: Python Server
```powershell
.\start-server.ps1
```
Then open: http://localhost:8000/index.html

### Option 2: Manual Python
```powershell
python -m http.server 8000
```
Then open: http://localhost:8000/index.html

### Option 3: VS Code Live Server Extension
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

## ❓ Why a Server?

Browsers block loading local `.vrm` files directly (CORS security).
You need a local server to load the 3D model file.

## 📝 What You Get

The report shows exactly what you can control:
- Expression names: `vrm.expressionManager.setValue('happy', 1.0)`
- Bone names: `vrm.humanoid.getRawBoneNode('leftHand')`
- Material info, mesh stats, and more!

---

**No npm install needed!** Just run `start.ps1` and go! 🚀
