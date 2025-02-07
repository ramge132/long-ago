<template>
  <div
    v-show="isVisible"
    id="tiger-animation"
    class="fixed inset-0 flex flex-col items-center justify-center overflow-hidden bg-[#f4b28bee] z-50"
    :class="{ 'fade-out': !isVisible }"
  >
    <img
      id="tiger"
      src="@/assets/tiger.gif"
      alt="Tiger"
      class="tiger-gif w-48 h-auto"
    />

    <!-- 순차적으로 등장하는 텍스트 -->
    <div
      id="tiger-text"
      class="tiger-text flex gap-2 mt-5 text-white font-makgeolli text-6xl"
    >
      <span class="word" style="animation-delay: 0s">아주</span>
      <span class="word" style="animation-delay: 1s">먼</span>
      <span class="word" style="animation-delay: 2s">옛날</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const isVisible = ref(true);

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
  @apply opacity-0 transform translate-y-5;
  animation: text-fade 1s ease-out forwards;
}

@keyframes text-fade {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
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
