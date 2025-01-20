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
  ],
});

export default router;
