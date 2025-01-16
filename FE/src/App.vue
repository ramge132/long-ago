<template>
  <div
    class="bg-no-repeat bg-cover bg-center bg-fairytail-image w-screen h-screen flex flex-col justify-center items-center"
  >
    <div
      class="relative border-dashed border-2 border-black p-6 rounded-lg shadow-md w-2/3 h-3/4 bg-[#ffffff80] flex flex-col justify-center items-center"
    >
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
      <div
        v-if="route.path.split('/')[1] === 'auth'"
        @click="playGuest"
        class="absolute bottom-5 right-5 cursor-pointer"
      >
        게스트로 진행하기 ➜
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
import { useRoute } from "vue-router";
// import { TopBar, Footer } from "@/components";

const route = useRoute();

const playGuest = () => {
  console.log("playGuest!");
  const rand_no = Math.floor(Math.random() * 100000);
  localStorage.setItem(
    "userData",
    JSON.stringify({ nickname: `Guest_${rand_no}` }),
  );
  console.log(`Welcome Guest_${rand_no}`);
};
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
</style>
