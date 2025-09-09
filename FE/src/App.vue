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
    
    <!-- 메인 컨테이너 with 광고 -->
    <div class="main-container flex justify-center items-center gap-x-6 w-full h-5/6">
      <!-- 왼쪽 광고 -->
      <div class="ad-left hidden xl:block">
        <AdBanner ad-slot="left-sidebar" ad-format="vertical" />
      </div>
      
      <!-- 중앙 메인 콘텐츠 -->
      <div
        class="view rounded-lg w-4/5 xl:w-auto xl:flex-1 xl:max-w-6xl h-full max-h-[700px] min-w-[1000px] min-h-[600px] bg-[#ffffff70] border-[1px] border-white backdrop-blur-[15px] flex flex-col justify-center items-center"
      >
        <ToggleButton />

        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" @start-loading="startLoading" />
          </Transition>
        </RouterView>
      </div>
      
      <!-- 오른쪽 광고 -->
      <div class="ad-right hidden xl:block">
        <AdBanner ad-slot="right-sidebar" ad-format="vertical" />
      </div>
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

    <Transition name="fade">
      <AnnouncementBox />
    </Transition>
  </div>
</template>

<script setup>
import { AnnouncementBox, TigerAnimation } from "./components";
import { ref, computed, Transition, watch } from "vue";
import { useAudioStore } from "./stores/audio";
import { useRoute } from "vue-router";
import { LoadingMusic } from "./assets";
import { TermsOfService, TopBar, FooterBar, ToggleButton, EBook, AdBanner } from "@/components";

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
    loadingMusic.volume = audioStore.audioVolume;  // 볼륨 적용
    if (data.value) {
      loadingMusic.play();
      audioStore.audioPlay = false;
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

/* 광고 영역 스타일 */
.main-container {
  max-width: 100vw;
  padding: 0 20px;
}

.ad-left, .ad-right {
  width: 320px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 반응형 스타일 */
@media (max-width: 1536px) {
  .ad-left, .ad-right {
    width: 280px;
  }
}

@media (max-width: 1400px) {
  .ad-left, .ad-right {
    width: 250px;
  }
}

/* XL 미만에서는 광고 숨김 */
@media (max-width: 1279px) {
  .main-container {
    padding: 0;
  }
  
  .view {
    width: 80% !important;
  }
}
</style>
