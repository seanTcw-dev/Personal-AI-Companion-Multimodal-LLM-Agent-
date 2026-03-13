import * as THREE from 'three';
import { model, scene } from './viewer.js';

// Animation state variables
let currentAnimation = null;
let animationMixer = null;
const animations = {};
let headBone, neckBone, spineBone, leftArmBone, rightArmBone, leftLegBone, rightLegBone;
let initialRotations = {};

// Set up the model controls
export function setupModelControls() {
    console.log('Setting up model controls');
    
    // Find and store important bones for animations
    findModelBones();
    
    // Set up command execution
    setupCommandInput();
    
    // Set up action buttons
    setupActionButtons();
    
    // Create event to signal model is fully loaded and ready
    const event = new Event('modelLoaded');
    document.dispatchEvent(event);
}

// Find and store important bones for animations
function findModelBones() {
    if (!model || !model.humanoid) {
        console.warn('Model or humanoid not available for bone mapping');
        return;
    }
    
    // Try to get important bones for animation
    try {
        // Get the bone nodes from the VRM humanoid
        headBone = model.humanoid.getNormalizedBoneNode('head');
        neckBone = model.humanoid.getNormalizedBoneNode('neck');
        spineBone = model.humanoid.getNormalizedBoneNode('spine');
        leftArmBone = model.humanoid.getNormalizedBoneNode('leftUpperArm');
        rightArmBone = model.humanoid.getNormalizedBoneNode('rightUpperArm');
        leftLegBone = model.humanoid.getNormalizedBoneNode('leftUpperLeg');
        rightLegBone = model.humanoid.getNormalizedBoneNode('rightUpperLeg');
        
        // Store initial rotations
        if (headBone) initialRotations.head = headBone.rotation.clone();
        if (neckBone) initialRotations.neck = neckBone.rotation.clone();
        if (spineBone) initialRotations.spine = spineBone.rotation.clone();
        if (leftArmBone) initialRotations.leftArm = leftArmBone.rotation.clone();
        if (rightArmBone) initialRotations.rightArm = rightArmBone.rotation.clone();
        if (leftLegBone) initialRotations.leftLeg = leftLegBone.rotation.clone();
        if (rightLegBone) initialRotations.rightLeg = rightLegBone.rotation.clone();
        
        console.log('Model bones mapped successfully');
    } catch (error) {
        console.error('Error mapping model bones:', error);
    }
}

// Set up the command input functionality
function setupCommandInput() {
    const commandInput = document.getElementById('command-input');
    const executeButton = document.getElementById('execute-command');
    
    if (!commandInput || !executeButton) {
        console.warn('Command input elements not found');
        return;
    }
    
    executeButton.addEventListener('click', () => {
        const command = commandInput.value.trim().toLowerCase();
        executeCommand(command);
    });
    
    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const command = commandInput.value.trim().toLowerCase();
            executeCommand(command);
        }
    });
}

// Set up action buttons
function setupActionButtons() {
    const actionButtons = {
        'btn-wave': () => executeCommand('wave'),
        'btn-nod': () => executeCommand('nod'),
        'btn-jump': () => executeCommand('jump'),
        'btn-dance': () => executeCommand('dance'),
        'btn-smile': () => executeCommand('smile'),
        'btn-reset': () => executeCommand('reset')
    };
    
    // Add event listeners to each button
    for (const [btnId, action] of Object.entries(actionButtons)) {
        const button = document.getElementById(btnId);
        if (button) {
            button.addEventListener('click', action);
        }
    }
}

// Execute a command to control the model
export function executeCommand(command) {
    console.log('Executing command:', command);
    
    // Stop any current animation
    stopCurrentAnimation();
    
    // Execute the appropriate command
    switch (command) {
        case 'wave':
            waveAnimation();
            break;
        case 'nod':
            nodAnimation();
            break;
        case 'jump':
            jumpAnimation();
            break;
        case 'dance':
            danceAnimation();
            break;
        case 'smile':
            smileExpression();
            break;
        case 'reset':
            resetModel();
            break;
        default:
            console.log('Unknown command:', command);
            // Try to parse more complex commands here if needed
            break;
    }
}

// Stop the current animation
function stopCurrentAnimation() {
    if (currentAnimation) {
        clearTimeout(currentAnimation);
        currentAnimation = null;
    }
    
    if (animationMixer) {
        animationMixer.stopAllAction();
    }
}

// Wave animation
function waveAnimation() {
    if (!rightArmBone) {
        console.warn('Right arm bone not found for wave animation');
        return;
    }
    
    const duration = 2000; // ms
    const startTime = Date.now();
    const initialRotation = initialRotations.rightArm ? initialRotations.rightArm.clone() : new THREE.Euler();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            // Simple wave animation
            rightArmBone.rotation.z = initialRotation.z + Math.sin(progress * Math.PI * 4) * 0.5;
            rightArmBone.rotation.x = initialRotation.x - 1.2; // Raise arm
            
            currentAnimation = setTimeout(animate, 16);
        } else {
            // Reset to initial rotation when done
            rightArmBone.rotation.copy(initialRotation);
            currentAnimation = null;
        }
    }
    
    animate();
}

// Nod animation
function nodAnimation() {
    if (!headBone) {
        console.warn('Head bone not found for nod animation');
        return;
    }
    
    const duration = 1500; // ms
    const startTime = Date.now();
    const initialRotation = initialRotations.head ? initialRotations.head.clone() : new THREE.Euler();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            // Simple nod animation
            headBone.rotation.x = initialRotation.x + Math.sin(progress * Math.PI * 3) * 0.3;
            
            currentAnimation = setTimeout(animate, 16);
        } else {
            // Reset to initial rotation when done
            headBone.rotation.copy(initialRotation);
            currentAnimation = null;
        }
    }
    
    animate();
}

// Jump animation
function jumpAnimation() {
    if (!model || !model.scene) {
        console.warn('Model not available for jump animation');
        return;
    }
    
    const duration = 1000; // ms
    const startTime = Date.now();
    const initialY = model.scene.position.y;
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            // Simple jump animation
            model.scene.position.y = initialY + Math.sin(progress * Math.PI) * 0.5;
            
            currentAnimation = setTimeout(animate, 16);
        } else {
            // Reset to initial position when done
            model.scene.position.y = initialY;
            currentAnimation = null;
        }
    }
    
    animate();
}

// Dance animation (more complex combination of movements)
function danceAnimation() {
    if (!model || !model.scene) {
        console.warn('Model not available for dance animation');
        return;
    }
    
    const duration = 3000; // ms
    const startTime = Date.now();
    
    // Store initial positions/rotations
    const initialPos = model.scene.position.clone();
    const initialHeadRot = headBone ? headBone.rotation.clone() : new THREE.Euler();
    const initialLeftArmRot = leftArmBone ? leftArmBone.rotation.clone() : new THREE.Euler();
    const initialRightArmRot = rightArmBone ? rightArmBone.rotation.clone() : new THREE.Euler();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            // Combined dance animation
            model.scene.position.y = initialPos.y + Math.sin(progress * Math.PI * 4) * 0.2;
            
            if (headBone) {
                headBone.rotation.y = initialHeadRot.y + Math.sin(progress * Math.PI * 2) * 0.3;
            }
            
            if (leftArmBone) {
                leftArmBone.rotation.z = initialLeftArmRot.z + Math.sin(progress * Math.PI * 3 + Math.PI) * 0.5;
                leftArmBone.rotation.x = initialLeftArmRot.x - 0.8;
            }
            
            if (rightArmBone) {
                rightArmBone.rotation.z = initialRightArmRot.z + Math.sin(progress * Math.PI * 3) * 0.5;
                rightArmBone.rotation.x = initialRightArmRot.x - 0.8;
            }
            
            currentAnimation = setTimeout(animate, 16);
        } else {
            // Reset everything when done
            model.scene.position.copy(initialPos);
            
            if (headBone) headBone.rotation.copy(initialHeadRot);
            if (leftArmBone) leftArmBone.rotation.copy(initialLeftArmRot);
            if (rightArmBone) rightArmBone.rotation.copy(initialRightArmRot);
            
            currentAnimation = null;
        }
    }
    
    animate();
}

// Smile expression (if model has blendshapes/morphs)
function smileExpression() {
    if (!model || !model.expressionManager) {
        console.warn('Model expression manager not available');
        return;
    }
    
    try {
        // Try to set a smile expression
        model.expressionManager.setValue('happy', 1.0);
        
        // Reset after 2 seconds
        currentAnimation = setTimeout(() => {
            model.expressionManager.setValue('happy', 0.0);
            currentAnimation = null;
        }, 2000);
        
    } catch (error) {
        console.error('Error setting smile expression:', error);
    }
}

// Reset model to initial state
function resetModel() {
    if (!model) {
        console.warn('Model not available for reset');
        return;
    }
    
    // Reset position
    if (model.scene) {
        model.scene.position.set(0, 0, 0);
    }
    
    // Reset all bone rotations
    if (initialRotations.head && headBone) headBone.rotation.copy(initialRotations.head);
    if (initialRotations.neck && neckBone) neckBone.rotation.copy(initialRotations.neck);
    if (initialRotations.spine && spineBone) spineBone.rotation.copy(initialRotations.spine);
    if (initialRotations.leftArm && leftArmBone) leftArmBone.rotation.copy(initialRotations.leftArm);
    if (initialRotations.rightArm && rightArmBone) rightArmBone.rotation.copy(initialRotations.rightArm);
    if (initialRotations.leftLeg && leftLegBone) leftLegBone.rotation.copy(initialRotations.leftLeg);
    if (initialRotations.rightLeg && rightLegBone) rightLegBone.rotation.copy(initialRotations.rightLeg);
    
    // Reset expressions if available
    if (model.expressionManager) {
        const expressions = ['happy', 'angry', 'sad', 'surprised', 'neutral'];
        expressions.forEach(exp => {
            try {
                model.expressionManager.setValue(exp, 0);
            } catch (e) {
                // Expression might not exist, ignore
            }
        });
    }
    
    console.log('Model reset to initial state');
}