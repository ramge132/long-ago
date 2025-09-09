import { createApp } from "vue";
import { createPinia } from "pinia";
// Toast plugin
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

import App from "./App.vue";
import router from "./router";
import "./assets/index.css";
import { initializeAds } from "./utils/adConfig";

const app = createApp(App);

app.use(createPinia());
app.use(router);

const options = {};
app.use(Toast, options);

// 광고 초기화
initializeAds();

app.mount("#app");