import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vue3GoogleLogin from 'vue3-google-login'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Add Pinia store to the application
app.use(createPinia())

// Add Router
app.use(router)

// Add Google Login - Using environment variable for security
app.use(vue3GoogleLogin, {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID
})

// Mount the app
app.mount('#app')
