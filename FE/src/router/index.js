import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Intro",
      component: () => import("@/views/IntroView.vue"),
      children: [
        // {
        //   path: '/init',
        //   name: 'Init',
        //   component: () => import('@/components/InitView.vue'),
        //   beforeEnter: (to, from, next) => {
        //   }
        // },
      ],
    },
    {
      path: "/init",
      name: "Init",
      component: () => import("@/views/InitView.vue"),
      beforeEnter: (to, from, next) => {
        if (!JSON.parse(localStorage.getItem("userData"))) {
          // if (true) {
          // 토큰이 없으면 로그인 페이지로 리다이렉트
          next({ name: "Auth" });
        } else {
          // 토큰이 있으면 다음 페이지로 이동
          next();
        }
      },
    },
    {
      path: "/auth",
      name: "Auth",
      component: () => import("@/views/AuthView.vue"),
    },
  ],
});

export default router;
