# Implementation Instructions for Anime Model Chatbot Project

This document outlines the implementation steps for building the full-stack AI chatbot application with a 3D character interface. These instructions are meant for the developer (you) as a guide for what needs to be implemented.

## Stage 1: Project Scaffolding & Backend Foundation

### Task 1.1: Project Structure & "Hello World" Backend
- [x] Create the backend directory structure
- [x] Create a minimal FastAPI application in backend/app/main.py with a root endpoint
- [x] Create backend/requirements.txt with necessary dependencies

### Task 1.2: WebSocket Implementation
- [x] Create backend/app/api/websockets.py with ConnectionManager class
- [x] Implement WebSocket endpoint for chat at /ws/chat/{user_id}
- [x] Update backend/app/main.py to include the WebSocket endpoint
- [x] Create backend/run.py script to run the FastAPI server

## Stage 2: Frontend Foundation

### Task 2.1: Component Structure Setup
- [x] Create necessary directories in frontend/src/components/ (chat, character, camera, layout)
- [x] Create service directory for WebSocket service
- [x] Create stores directory for Pinia state management

### Task 2.2: Three-Column Layout
- [x] Create TheMainLayout.vue with a three-column layout using CSS Flexbox/Grid
- [x] Update frontend/src/App.vue to use the TheMainLayout component

### Task 2.3: 3D Stage Setup (CharacterView)
- [x] Update package.json to include Three.js and @pixiv/three-vrm
- [x] Create frontend/src/components/character/CharacterView.vue
- [x] Set up a basic Three.js scene with lights and camera
- [x] Create functions to load and display a VRM model
- [x] Implement setExpression function to control character expressions
- [x] Expose the setExpression function using defineExpose

### Task 2.4: Chat Interface
- [x] Create frontend/src/components/chat/ChatView.vue
- [x] Implement message display and input functionality

### Task 2.5: Camera View
- [x] Create frontend/src/components/camera/CameraView.vue
- [x] Implement camera access and display functionality

## Stage 3: Integration & State Management

### Task 3.1: WebSocket Service
- [x] Create frontend/src/services/websocket.js
- [x] Implement connect and sendMessage methods
- [x] Implement message handling

### Task 3.2: Chat Store
- [x] Create frontend/src/stores/chatStore.js
- [x] Implement messages array and currentEmotion state
- [x] Add addMessage and setEmotion actions

### Task 3.3: Connect Chat to Character
- [x] In TheMainLayout.vue, watch for changes to chatStore.currentEmotion
- [x] Call setExpression on the character component when emotion changes

## Stage 4: Final Integration & Testing

### Task 4.1: Main App Entry Point
- [x] Update main.js to include Pinia
- [x] Clean up the App.vue and add global styles

### Task 4.2: Package.json Updates
- [x] Update package.json with all necessary dependencies
- [x] Ensure scripts are properly configured

### Task 4.3: Documentation
- [x] Create README.md with project overview and setup instructions
- [x] Document architecture and usage

## Notes
- The frontend already has a basic Vue 3 + Vite project structure
- We are not implementing any SQL/database functionality
- The backend will provide a simple echo response for now
- The implementation should follow modern JavaScript/Vue practices using the Composition API

## Next Steps After Implementation
1. Test the WebSocket connection between frontend and backend
2. Test character expressions based on chat messages
3. Add a sample VRM model to frontend/public/
4. Enhance the backend to provide more intelligent responses

## Outstanding Tasks
- [x] Create frontend/src/stores/chatStore.js for state management
- [x] Create setup and run scripts for easy deployment
- [ ] Acquire and add a sample VRM model to frontend/public/avatar.vrm

## Implementation References

### Stage 1: Backend (FastAPI)
- FastAPI Documentation: https://fastapi.tiangolo.com/
- WebSockets in FastAPI: https://fastapi.tiangolo.com/advanced/websockets/

### Stage 2: Frontend (Vue 3 + Vite)
- Vue 3 Documentation: https://v3.vuejs.org/
- Vite Documentation: https://vitejs.dev/
- Composition API: https://v3.vuejs.org/guide/composition-api-introduction.html

### Stage 3: 3D Character (Three.js + VRM)
- Three.js Documentation: https://threejs.org/docs/
- Three-VRM Documentation: https://github.com/pixiv/three-vrm

### Stage 4: State Management (Pinia)
- Pinia Documentation: https://pinia.vuejs.org/

This implementation follows the requirements from the project specification with the goal of creating a functional, real-time interactive chatbot with a 3D character interface.