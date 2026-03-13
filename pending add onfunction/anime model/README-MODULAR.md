# VRM Model Viewer - Modular Structure

This project is a simple web viewer for VRM 3D models using Three.js and the @pixiv/three-vrm library, organized with a modular code structure.

## Project Structure

The code is organized into three main JavaScript files:

1. **main.js** - Entry point that initializes the application
2. **viewer.js** - Core scene setup, camera, lighting, and rendering
3. **model-controls.js** - Handles model animations and user interaction

This modular structure makes the code:
- Easier to maintain
- More organized
- Easier to extend with new features

## Features

- Load and display VRM models
- Upload custom VRM models
- Basic animations: wave, nod, jump, dance
- Expression control (if model supports it)
- Camera controls (orbit, pan, zoom)

## How to Use

1. Open the `index.html` file in your web browser or run a local web server.
2. The default model will load automatically.
3. Use the control panel to:
   - Type commands in the text box
   - Click animation buttons
   - Reset the model to its initial state
4. Upload your own VRM models using the "Load VRM Model" button.

## Available Commands

- **wave** - Makes the model wave its right arm
- **nod** - Makes the model nod its head
- **jump** - Makes the model jump up and down
- **dance** - Plays a simple dance animation
- **smile** - Changes facial expression to smile (if supported by the model)
- **reset** - Resets the model to its initial state

## Technical Details

### viewer.js
Handles the core 3D rendering functionality:
- Scene setup
- Camera and lighting
- Model loading
- Rendering loop
- Window resize handling

### model-controls.js
Handles all model interactions:
- Animation system
- Bone manipulation
- Expression control
- Command processing

## Using a Local Web Server

For security reasons, modern browsers may block loading local files directly. Try using a simple local web server:

```
# Navigate to the project folder
cd "c:\Users\SeanTeng\Desktop\anime model"

# Python 3
python -m http.server 8000

# Then open http://localhost:8000 in your browser
```

## Extending the Project

To add new animations or features:
1. Add new animation functions in `model-controls.js`
2. Register new commands in the `executeCommand` function
3. Add UI controls in `index.html` if needed

## Credits

This project uses:
- Three.js for 3D rendering
- @pixiv/three-vrm for loading and handling VRM models