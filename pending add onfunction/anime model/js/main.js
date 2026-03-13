import { initViewer, startRenderLoop, setupFileInput } from './viewer.js';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing VRM model viewer application');
    
    // Initialize the 3D viewer
    initViewer();
    
    // Start the render loop
    startRenderLoop();
    
    // Setup file input for loading custom models
    setupFileInput();
});