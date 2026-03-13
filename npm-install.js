// npm-install.js
// This script installs frontend dependencies from the root directory
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Frontend directory path relative to root
const frontendDir = path.join(__dirname, 'frontend');

// Check if the frontend directory exists
if (!fs.existsSync(frontendDir)) {
    console.error('Frontend directory not found!');
    process.exit(1);
}

try {
    console.log('Installing frontend dependencies...');
    try {
        // First try normal installation
        execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });
    } catch (firstError) {
        // If that fails, try with legacy peer deps
        console.log('Initial installation failed, trying with --legacy-peer-deps...');
        execSync('npm install --legacy-peer-deps', { cwd: frontendDir, stdio: 'inherit' });
    }
    console.log('Frontend dependencies installed successfully.');
} catch (error) {
    console.error('Failed to install frontend dependencies:', error.message);
    process.exit(1);
}