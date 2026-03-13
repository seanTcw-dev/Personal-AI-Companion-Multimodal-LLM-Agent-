# Project Setup Instructions

This document provides detailed instructions for setting up the Anime Model Chatbot project on Windows.

## Simplified Setup (Recommended)

### 1. One-Step Installation

Simply double-click on `install-all.bat` or run it from a command prompt:
```
install-all.bat
```

This script will:
- Create a Python virtual environment named 'aniChatbot' (or use it if it already exists)
- Install all Python dependencies
- Set up Node.js within the same environment
- Install all frontend dependencies automatically

### 2. Running the Application

Double-click on `start.bat` or run it from a command prompt:
```
start.bat
```

This will:
- Start the backend server at http://localhost:8000
- Start the frontend development server at http://localhost:5173

## Manual Setup (if needed)

This will install all the required packages listed in package.json, including:
- Vue.js 3
- Pinia (for state management)
- Three.js (for 3D rendering)
- @pixiv/three-vrm (for VRM model support)

### 2. Add a VRM Model

For the 3D character to work, you need to add a VRM model file:

1. Download a VRM model file (you can find free ones at [VRoid Hub](https://hub.vroid.com/) or [The Seed Online](https://seed.online/))
2. Rename it to `avatar.vrm`
3. Place it in the `frontend/public/` directory

### 3. Run the Frontend Development Server

```bash
# Make sure you're in the frontend directory
npm run dev
```

The frontend development server will start at http://localhost:5173 (or another port if 5173 is already in use).

## Troubleshooting

### Common Issues

1. **Dependency Installation Errors**:
   - For frontend: Make sure Node.js (v14+) is installed
   - For backend: Make sure Python (v3.8+) is installed

2. **"Module not found" Errors**:
   - Verify that all dependencies are installed
   - For frontend issues: Run `npm install` again
   - For backend issues: Make sure the virtual environment is activated

3. **WebSocket Connection Errors**:
   - Ensure both frontend and backend servers are running
   - Check that the WebSocket URL in `frontend/src/services/websocket.js` matches the backend URL

4. **3D Model Loading Issues**:
   - Make sure you've added a valid VRM file named `avatar.vrm` to the `frontend/public/` directory
   - Check the browser console for specific errors

For any other issues, please refer to the documentation for the specific technologies used in this project:
- [Vue.js](https://vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)
- [Three.js](https://threejs.org/)
- [VRM](https://vrm.dev/en/)
- [FastAPI](https://fastapi.tiangolo.com/)