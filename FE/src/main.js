import { createApp } from "vue";
import { createPinia } from "pinia";
// Toast plugin
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

import App from "./App.vue";
import router from "./router";
import "./assets/index.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);

const options = {};
app.use(Toast, options);

app.mount("#app");

const customCursor = document.querySelector(".custom-cursor");

// 마우스 이동에 따른 커서 위치 업데이트
document.body.addEventListener("mousemove", (e) => {
  // `pointer` 상태가 되면 커서 애니메이션 활성화
  const isPointerActive = e.target.style.cursor === "pointer";
  if (isPointerActive) {
    document.body.classList.add("pointer-active");
  } else {
    document.body.classList.remove("pointer-active");
  }

  // 커서 위치 업데이트
  customCursor.style.left = `${e.pageX - customCursor.offsetWidth / 2}px`;
  customCursor.style.top = `${e.pageY - customCursor.offsetHeight / 2}px`;
});
