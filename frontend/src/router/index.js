import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../views/LandingPage.vue';
import SignInPage from '../views/SignInPage.vue';
import TheMainLayout from '../components/layout/TheMainLayout.vue';
import UserProfileSettings from '../views/UserProfileSettings.vue';
import VoiceSettings from '../views/VoiceSettings.vue';
import ModelSettings from '../views/ModelSettings.vue';
import EmailView from '../views/EmailView.vue';

const routes = [
    {
        path: '/',
        name: 'Landing',
        component: LandingPage
    },
    {
        path: '/login',
        name: 'SignIn',
        component: SignInPage
    },
    {
        path: '/chat',
        name: 'Chat',
        component: TheMainLayout,
        // Add meta field to indicate protected route if we add auth guard later
        meta: { requiresAuth: true }
    },
    {
        path: '/settings/profile',
        name: 'UserProfileSettings',
        component: UserProfileSettings,
        meta: { requiresAuth: true }
    },
    {
        path: '/settings/voice',
        name: 'VoiceSettings',
        component: VoiceSettings,
        meta: { requiresAuth: true }
    },
    {
        path: '/settings/model',
        name: 'ModelSettings',
        component: ModelSettings,
        meta: { requiresAuth: true }
    },
    {
        path: '/email',
        name: 'EmailClient',
        component: EmailView,
        meta: { requiresAuth: true }
    },
    {
        path: '/desktop-pet',
        name: 'DesktopPet',
        component: () => import('../views/DesktopPetView.vue'), // Lazy load
        meta: { requiresAuth: true, layout: 'blank' }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
