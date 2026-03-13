import { createApp } from 'vue';
import ModelInspector from './components/debug/ModelInspector.vue';
import './style.css';

const app = createApp(ModelInspector);
app.mount('#app');
