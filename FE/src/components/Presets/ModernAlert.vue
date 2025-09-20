<template>
  <div
    v-if="isVisible"
    class="modern-alert-overlay fixed inset-0 z-[9999] flex items-center justify-center pointer-events-none"
  >
    <div
      class="modern-alert-container relative transform transition-all duration-700 ease-out pointer-events-auto"
      :class="animationClass"
    >
      <!-- Background with glassmorphism effect -->
      <div class="modern-alert-bg absolute inset-0 rounded-3xl backdrop-blur-2xl bg-gradient-to-br from-white/30 to-white/10 border border-white/20 shadow-2xl"></div>

      <!-- Content -->
      <div class="modern-alert-content relative z-10 p-8 text-center">
        <!-- Icon with floating animation -->
        <div class="modern-alert-icon mb-6 relative">
          <div class="absolute inset-0 rounded-full bg-gradient-to-r from-red-400 to-orange-500 opacity-20 animate-ping"></div>
          <div class="relative w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center shadow-lg">
            <svg class="w-10 h-10 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <!-- Title -->
        <h2 class="modern-alert-title text-3xl font-bold text-gray-800 mb-4 font-katuri">
          🔥 긴장감 100% 도달! 🔥
        </h2>

        <!-- Message -->
        <p class="modern-alert-message text-lg text-gray-700 mb-6 font-katuri leading-relaxed">
          {{ message }}
        </p>

        <!-- Decorative line -->
        <div class="w-24 h-1 bg-gradient-to-r from-red-400 to-orange-500 rounded-full mx-auto mb-6"></div>

        <!-- Button -->
        <button
          @click="closeAlert"
          class="modern-alert-button px-8 py-3 bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-600 hover:to-orange-700 text-white font-bold rounded-2xl transform transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95 font-katuri"
        >
          이제 결말을 맺어주세요! ✨
        </button>
      </div>

      <!-- Floating particles effect -->
      <div class="modern-alert-particles absolute inset-0 pointer-events-none">
        <div class="particle particle-1"></div>
        <div class="particle particle-2"></div>
        <div class="particle particle-3"></div>
        <div class="particle particle-4"></div>
        <div class="particle particle-5"></div>
        <div class="particle particle-6"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: '긴장감이 100%에 도달했습니다!\n이제 결말을 맺어야 할 때입니다!'
  },
  duration: {
    type: Number,
    default: 5000 // 5초 후 자동으로 닫힘
  }
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
const isAnimating = ref(false)

const animationClass = computed(() => {
  if (isAnimating.value) {
    return 'scale-110 opacity-100'
  }
  return 'scale-95 opacity-90'
})

const show = async () => {
  isVisible.value = true
  await nextTick()
  setTimeout(() => {
    isAnimating.value = true
  }, 50)

  // 자동으로 닫기 (duration이 0보다 클 때)
  if (props.duration > 0) {
    setTimeout(() => {
      closeAlert()
    }, props.duration)
  }
}

const closeAlert = () => {
  isAnimating.value = false
  setTimeout(() => {
    isVisible.value = false
    emit('close')
  }, 300)
}

onMounted(() => {
  show()
})

defineExpose({
  show,
  closeAlert
})
</script>

<style scoped>
/* 오버레이 배경 - 블러 효과 없이 투명 */
.modern-alert-overlay {
  background: transparent;
  animation: fadeIn 0.5s ease-out;
}

/* 메인 컨테이너 */
.modern-alert-container {
  width: 400px;
  max-width: 90vw;
  min-height: 350px;
}

/* 배경 glassmorphism */
.modern-alert-bg {
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 1px 0 rgba(255, 255, 255, 0.2) inset;
}

/* 아이콘 효과 */
.modern-alert-icon {
  animation: float 3s ease-in-out infinite;
}

/* 텍스트 스타일 */
.modern-alert-title {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modern-alert-message {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 버튼 효과 */
.modern-alert-button {
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-alert-button:hover {
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

/* 플로팅 파티클 */
.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: linear-gradient(45deg, #f59e0b, #ef4444);
  border-radius: 50%;
  opacity: 0.6;
  animation: particle-float 4s ease-in-out infinite;
}

.particle-1 {
  top: 20%;
  left: 15%;
  animation-delay: 0s;
  animation-duration: 3s;
}

.particle-2 {
  top: 30%;
  right: 20%;
  animation-delay: 0.5s;
  animation-duration: 4s;
}

.particle-3 {
  bottom: 25%;
  left: 25%;
  animation-delay: 1s;
  animation-duration: 3.5s;
}

.particle-4 {
  bottom: 35%;
  right: 15%;
  animation-delay: 1.5s;
  animation-duration: 4.5s;
}

.particle-5 {
  top: 50%;
  left: 10%;
  animation-delay: 2s;
  animation-duration: 3.2s;
}

.particle-6 {
  top: 60%;
  right: 30%;
  animation-delay: 2.5s;
  animation-duration: 3.8s;
}

/* 애니메이션 키프레임 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes particle-float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0.6;
  }
  25% {
    transform: translateY(-15px) translateX(5px);
    opacity: 1;
  }
  50% {
    transform: translateY(-8px) translateX(-3px);
    opacity: 0.8;
  }
  75% {
    transform: translateY(-20px) translateX(8px);
    opacity: 0.9;
  }
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .modern-alert-container {
    width: 350px;
    margin: 20px;
  }

  .modern-alert-content {
    padding: 6rem 1.5rem;
  }

  .modern-alert-title {
    font-size: 1.75rem;
  }

  .modern-alert-message {
    font-size: 1rem;
  }
}

/* 다크모드 대응 */
@media (prefers-color-scheme: dark) {
  .modern-alert-bg {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.4) 0%, rgba(20, 20, 20, 0.2) 100%);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .modern-alert-title {
    background: linear-gradient(135deg, #f7fafc 0%, #e2e8f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .modern-alert-message {
    color: #e2e8f0;
  }
}
</style>