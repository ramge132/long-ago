<template>
  <div
    v-if="isVisible"
    id="tiger-animation"
    class="fixed inset-0 flex flex-col items-center justify-center overflow-hidden bg-[#0000008c] z-50"
    :class="{ 'fade-out': !isVisible }"
  >
    <img
      id="tiger"
      src="@/assets/ink.gif"
      alt="Tiger"
      class="min-w-full min-h-full fixed"
    />

    <!-- 순차적으로 등장하는 텍스트 -->
    <div
      id="tiger-text"
      class="tiger-text flex gap-2 mt-5 p-1 text-black font-logoFont text-6xl absolute -translate-x-[5%] translate-y-[150%] overflow-hidden"
    >
      <span class="word" :style="{ animationDelay: swing ? '0s' : '0.6s'}" :class="swing ? 'swing' : ''">L</span>
      <span class="word" :style="{ animationDelay: swing ? '0s' : '0.7s'}" :class="swing ? 'swing' : ''">O</span>
      <span class="word" :style="{ animationDelay: swing ? '0s' : '0.8s'}" :class="swing ? 'swing' : ''">N</span>
      <span class="word" :style="{ animationDelay: swing ? '0s' : '0.9s'}" :class="swing ? 'swing' : ''">G&nbsp</span>
      <span class="word" :style="{ animationDelay: swing ? '0s' : '1s'}" :class="swing ? 'swing' : ''">A</span>
      <span class="word" :style="{ animationDelay: swing ? '0s' : '1.1s'}" :class="swing ? 'swing' : ''">G</span>
      <span class="word" :style="{ animationDelay: swing ? '0s' : '1.2s'}" :class="swing ? 'swing' : ''" @animationend="startSwing">O</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const isVisible = ref(true);
const swing = ref(false);

const startSwing = () => {
  swing.value = true;
}

onMounted(() => { 
  // 5초 후에 애니메이션을 적용하며 서서히 사라짐 
  setTimeout(() => {
    isVisible.value = false;
  }, 4000);
});
</script>

<style scoped>
/* 텍스트 애니메이션 */
.word { 
  @apply transform translate-y-80;
  color: white;
  text-shadow: 2px 2px 1px rgb(241, 163, 230);
  animation: text-fade 0.3s forwards;
}

.swing {
  transform: translateY(0);
  animation: swing 0.5s infinite;
}

@keyframes swing {
  0% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-5deg);
  }
  50% {
    transform: rotate(0deg);
  }
  75% {
    transform: rotate(5deg);
  }
  100% {
    transform: rotate(0deg);
  }
}

@keyframes text-fade {
  from {
    transform: translateY(80px);
  }
  to {
    transform: translateY(0);
  }
}

/* fade-out 애니메이션 */
.fade-out {
  animation: fade-out 2s forwards;
}

@keyframes fade-out {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}
</style>
