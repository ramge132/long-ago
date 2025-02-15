<template>
  <div
    class="bg-no-repeat bg-cover bg-center w-screen h-screen flex flex-col justify-center items-center relative"
    :class="backgroundClass"
  >
    <Transition name="fade-out">
      <TigerAnimation />
    </Transition>
    <Transition name="fade">
      <TopBar v-if="route.path === '/'" />
    </Transition>
    <div
      class="view rounded-lg w-4/5 h-5/6 max-w-6xl max-h-[700px] min-w-[1000px] min-h-[650px] bg-[#ffffff70] border-[1px] border-white backdrop-blur-[15px] flex flex-col justify-center items-center"
    >
      <ToggleButton />

      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </div>

    <Transition name="fade">
      <FooterBar v-if="route.path === '/'" />
    </Transition>
  </div>
</template>

<script setup>
import { TigerAnimation } from "./components";
import { computed } from "vue";
import { useRoute } from "vue-router";
import { TopBar, FooterBar, ToggleButton } from "@/components";

const route = useRoute();

const backgroundClass = computed(() => {
  switch (route.path) {
    case "/game/play":
      return "bg-game-image";
    default:
      return "bg-fairytail-image";
  }
});
</script>

<style>
/* Enter 애니메이션 (슬라이드 없이 나타남) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out; /* opacity로 부드럽게 나타남 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* 컴포넌트가 처음에는 안 보이게 설정 */
}

.view {
  box-shadow: 0 0 100px rgba(0, 0, 0, 0.23), inset 0 0 100px rgba(255, 255, 255, 0.23);
}
</style>
