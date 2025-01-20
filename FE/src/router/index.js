import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Intro",
      component: () => import("@/views/IntroView.vue"),
      children: [
        {
          path: '',
          name: 'Init',
          component: () => import('@/views/InitView.vue'),
        },
      ],
    },
  ],
});

export default router;
