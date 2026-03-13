import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin } from '@pixiv/three-vrm';
import { setupModelControls } from './model-controls.js';

// Global variables for scene management
export let camera, scene, renderer, controls;
export let model = null;
let clock = new THREE.Clock();

// Initialize the scene, camera, and renderer
export function initViewer() {
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // Create camera
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.5, 3);

    // Create light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 1, 1).normalize();
    scene.add(directionalLight);

    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.body.appendChild(renderer.domElement);

    // Add orbit controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.minDistance = 1;
    controls.maxDistance = 10;
    controls.target.set(0, 1, 0);
    controls.update();

    // Handle window resizing
    window.addEventListener('resize', onWindowResize);

    // Load VRM model
    loadVRMModel('../vmodels/AvatarSample_A.vrm');
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Load VRM model
export function loadVRMModel(modelPath) {
    // Create a GLTFLoader
    const loader = new GLTFLoader();

    // Import VRM extension
    loader.register((parser) => {
        return new VRMLoaderPlugin(parser);
    });

    console.log('Starting to load VRM model from:', modelPath);

    // Show loading message
    document.getElementById('loading').style.display = 'block';
    document.getElementById('loading').textContent = 'Loading model...';

    // Load VRM model
    loader.load(
        modelPath,
        (gltf) => {
            // Get VRM instance from gltf.userData.vrm
            const vrm = gltf.userData.vrm;
            
            if (vrm) {
                // Clean up previous model if exists
                if (model && model.scene) {
                    scene.remove(model.scene);
                }
                
                // Add the model to the scene
                model = vrm;
                scene.add(vrm.scene);
                
                // Hide loading message
                document.getElementById('loading').style.display = 'none';
                console.log('VRM model added to scene successfully');
                
                // Initialize controls after model is loaded
                setupModelControls();
            } else {
                console.error('VRM data not found in the loaded model');
                document.getElementById('loading').textContent = 'Error: Unable to load VRM data';
            }
        },
        (progress) => {
            const percent = (progress.loaded / progress.total) * 100;
            document.getElementById('loading').textContent = `Loading model... ${percent.toFixed(2)}%`;
        },
        (error) => {
            console.error('Error loading VRM model:', error);
            document.getElementById('loading').textContent = 'Error loading model. Check console for details.';
        }
    );
}

// Animation loop
export function startRenderLoop() {
    function animate() {
        requestAnimationFrame(animate);
        
        const deltaTime = clock.getDelta();
        
        // Update camera controls
        controls.update();
        
        // Update VRM model if it exists
        if (model && model.update) {
            model.update(deltaTime);
        }
        
        // Render scene
        renderer.render(scene, camera);
    }
    
    animate();
}

// Set up file input for loading custom models
export function setupFileInput() {
    const fileInput = document.getElementById('file-input');
    const loadButton = document.getElementById('load-model');
    
    loadButton.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const fileURL = URL.createObjectURL(file);
            loadVRMModel(fileURL);
            
            // Add cleanup for object URL
            document.addEventListener('modelLoaded', () => {
                URL.revokeObjectURL(fileURL);
            }, { once: true });
        }
    });
}