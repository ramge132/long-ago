import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Intro",
      component: () => import("@/views/IntroView.vue"),
      children: [
        {
          path: "",
          name: "Init",
          component: () => import("@/views/InitView.vue"),
        },
      ],
    },
    {
      path: "/game",
      name: "Game",
      component: () => import("@/views/GameView.vue"),
      beforeEnter: (to, from, next) => {
        const userStore = useUserStore();
        if (!userStore.userData.userNickname) {
          next({ name: "Init" });
        } else {
          next();
        }
      },
      children: [
        {
          path: "",
          name: "Lobby",
          component: () => import("@/views/Game/LobbyView.vue"),
        },
        {
          path: "play",
          name: "InGame",
          component: () => import("@/views/Game/LobbyView.vue"),
        },
      ]
    },
  ],
});

export default router;
