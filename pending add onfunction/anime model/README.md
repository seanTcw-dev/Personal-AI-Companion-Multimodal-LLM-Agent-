# VRM Model Viewer

This is a simple web viewer for VRM 3D models using Three.js and the @pixiv/three-vrm library.

## How to Use

1. Open the `index.html` file in your web browser. You can do this by:
   - Double-clicking the file
   - Right-clicking and selecting "Open with" and choosing your web browser
   - Or using a local web server (recommended for better security)

2. The viewer will automatically load the VRM model from the `vmodels` folder.

3. Interact with the model:
   - Left-click and drag to rotate the camera around the model
   - Right-click and drag to pan
   - Scroll wheel to zoom in and out

## Using a Local Web Server

For security reasons, modern browsers may block loading local files directly. If you encounter issues, try using a simple local web server:

### Using Python (if installed):

```
# Navigate to the project folder
cd "c:\Users\SeanTeng\Desktop\anime model"

# Python 3
python -m http.server

# Then open http://localhost:8000 in your browser
```

### Using Node.js (if installed):

```
# Install http-server globally (once)
npm install -g http-server

# Navigate to the project folder
cd "c:\Users\SeanTeng\Desktop\anime model"

# Start the server
http-server

# Then open http://localhost:8080 in your browser
```

## Customizing

To load a different VRM model:
1. Add your VRM model file to the `vmodels` folder
2. Edit the `js/main.js` file, changing the path in the `loadVRM()` function to point to your model file