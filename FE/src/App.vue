<template>
  <Transition name="fade-out">
    <TigerAnimation />
  </Transition>
  <div
    class="bg-no-repeat bg-cover bg-center w-screen h-screen flex flex-col justify-center items-center relative"
    :class="backgroundClass"
  >
    <Transition name="fade">
      <TopBar v-if="route.path === '/'" />
    </Transition>
    <div
      class="view rounded-lg w-4/5 h-5/6 max-w-6xl max-h-[700px] min-w-[1000px] min-h-[600px] bg-[#ffffff70] border-[1px] border-white backdrop-blur-[15px] flex flex-col justify-center items-center"
    >
      <ToggleButton />

      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" @start-loading="startLoading" />
        </Transition>
      </RouterView>
    </div>

    <Transition name="fade">
      <FooterBar v-if="route.path === '/'" @toggle-terms="toggleTerms" />
    </Transition>
    
    <Transition name="fade">
      <TermsOfService v-show="isTermsOfServiceOpened" @click="toggleTerms" />
    </Transition>

    <Transition name="fade">
      <div v-show="isLoading" class="absolute z-50 top-0 left-0 rounded-lg w-full h-full bg-[#ffffff30]">
        <img src="@/assets/loading.gif" alt="" class="w-full h-full object-cover">
      </div>
    </Transition>

    <Transition name="fade">
      <EBook v-if="isEBookOpened" :ISBN="route.query.ISBN" @close-e-book="closeEBook" />
    </Transition>
  </div>
</template>

<script setup>
import { TigerAnimation } from "./components";
import { ref, computed, Transition, watch } from "vue";
import { useAudioStore } from "./stores/audio";
import { useRoute } from "vue-router";
import { LoadingMusic } from "./assets";
import { TermsOfService, TopBar, FooterBar, ToggleButton, EBook } from "@/components";

// 로딩 애니메이션 보이는 여부
const isLoading = ref(false);
const isTermsOfServiceOpened = ref(false);
const isEBookOpened = ref(false);
const audioStore = useAudioStore();
const loadingMusic = new Audio(LoadingMusic);

const startLoading = (data) => {
  // 로딩 시작인 경우
  if (audioStore.audioData) {
    loadingMusic.loop = true;
    if (data.value) {
      loadingMusic.play();
      audioStore.audioPlay = false;
      console.log(audioStore.audioData);
    } else {
      loadingMusic.pause();
      loadingMusic.currentTime = 0;
      audioStore.audioPlay = true;
    }
  }
  isLoading.value = data.value;
};

const route = useRoute();

const backgroundClass = computed(() => {
  switch (route.path) {
    case "/game/play":
      return "bg-game-image";
    default:
      return "bg-fairytail-image";
  }
});

const toggleTerms = () => {
  isTermsOfServiceOpened.value = !isTermsOfServiceOpened.value
}

const closeEBook = () => {
  isEBookOpened.value = false;
};

watch(
  () => route.query.ISBN,
  (newISBN) => {
    if (newISBN) {
      isEBookOpened.value = true;
    }
  },
  { immediate: true } // 처음 마운트될 때도 실행
);
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
