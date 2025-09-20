<template>
  <div
    v-if="isVisible"
    class="small-alert-overlay fixed top-4 left-1/2 transform -translate-x-1/2 z-[9998] pointer-events-none"
  >
    <div
      class="small-alert-container relative transform transition-all duration-500 ease-out pointer-events-auto"
      :class="animationClass"
    >
      <!-- Background with glassmorphism effect -->
      <div class="small-alert-bg absolute inset-0 rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/30 to-white/10 border border-white/20 shadow-xl"></div>

      <!-- Content -->
      <div class="small-alert-content relative z-10 px-6 py-4 text-center">
        <!-- Icon with floating animation -->
        <div class="small-alert-icon mb-3 relative">
          <div class="absolute inset-0 rounded-full bg-gradient-to-r from-orange-400 to-yellow-500 opacity-20 animate-ping"></div>
          <div class="relative w-12 h-12 mx-auto rounded-full bg-gradient-to-br from-orange-500 to-yellow-600 flex items-center justify-center shadow-md">
            <svg class="w-6 h-6 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <!-- Title -->
        <h3 class="small-alert-title text-lg font-bold text-gray-800 mb-2 font-katuri">
          결말카드 사용 가능!
        </h3>

        <!-- Message -->
        <p class="small-alert-message text-sm text-gray-700 mb-3 font-katuri leading-snug">
          긴장감이 35%에 도달했습니다
        </p>

        <!-- Progress Bar (작은 버전) -->
        <div class="w-full mb-3" v-if="showProgress">
          <div class="bg-gray-200 rounded-full h-1 overflow-hidden">
            <div
              class="progress-bar h-full bg-gradient-to-r from-orange-500 to-yellow-600 rounded-full transition-all duration-100 ease-linear"
              :style="{ width: progressWidth + '%' }"
            ></div>
          </div>
          <p class="text-xs text-gray-500 text-center mt-1 font-katuri">
            {{ Math.ceil(remainingTime / 1000) }}초 후 자동으로 닫힙니다
          </p>
        </div>

        <!-- Decorative line -->
        <div class="w-16 h-0.5 bg-gradient-to-r from-orange-400 to-yellow-500 rounded-full mx-auto"></div>
      </div>

      <!-- Floating particles effect (작은 버전) -->
      <div class="small-alert-particles absolute inset-0 pointer-events-none">
        <div class="small-particle small-particle-1"></div>
        <div class="small-particle small-particle-2"></div>
        <div class="small-particle small-particle-3"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: '긴장감이 35%에 도달했습니다'
  },
  duration: {
    type: Number,
    default: 3000 // 3초 후 자동으로 닫힘
  },
  showProgress: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
const isAnimating = ref(false)
const progressWidth = ref(100)
const remainingTime = ref(props.duration)
let progressInterval = null
let autoCloseTimeout = null

const animationClass = computed(() => {
  if (isAnimating.value) {
    return 'scale-100 opacity-100 translate-y-0'
  }
  return 'scale-95 opacity-90 -translate-y-4'
})

const show = async () => {
  isVisible.value = true
  await nextTick()
  setTimeout(() => {
    isAnimating.value = true
  }, 50)

  // 자동으로 닫기 (duration이 0보다 클 때)
  if (props.duration > 0 && props.showProgress) {
    startProgressTimer()
    autoCloseTimeout = setTimeout(() => {
      closeAlert()
    }, props.duration)
  }
}

const startProgressTimer = () => {
  const interval = 100 // 100ms마다 업데이트
  const totalSteps = props.duration / interval
  let currentStep = 0

  progressInterval = setInterval(() => {
    currentStep++
    const progress = ((totalSteps - currentStep) / totalSteps) * 100
    progressWidth.value = Math.max(0, progress)
    remainingTime.value = Math.max(0, props.duration - (currentStep * interval))

    if (currentStep >= totalSteps) {
      clearInterval(progressInterval)
    }
  }, interval)
}

const closeAlert = () => {
  // 타이머들 정리
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
  if (autoCloseTimeout) {
    clearTimeout(autoCloseTimeout)
    autoCloseTimeout = null
  }

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
/* 오버레이 배경 - 투명 */
.small-alert-overlay {
  animation: slideDown 0.5s ease-out;
}

/* 메인 컨테이너 - 작은 크기 */
.small-alert-container {
  width: 280px;
  max-width: 90vw;
}

/* 배경 glassmorphism */
.small-alert-bg {
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 1px 0 rgba(255, 255, 255, 0.2) inset;
}

/* 아이콘 효과 */
.small-alert-icon {
  animation: float 2s ease-in-out infinite;
}

/* 텍스트 스타일 */
.small-alert-title {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.small-alert-message {
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

/* 작은 플로팅 파티클 */
.small-particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: linear-gradient(45deg, #f59e0b, #eab308);
  border-radius: 50%;
  opacity: 0.6;
  animation: small-particle-float 3s ease-in-out infinite;
}

.small-particle-1 {
  top: 20%;
  left: 20%;
  animation-delay: 0s;
  animation-duration: 2.5s;
}

.small-particle-2 {
  top: 70%;
  right: 25%;
  animation-delay: 0.8s;
  animation-duration: 3s;
}

.small-particle-3 {
  bottom: 30%;
  left: 70%;
  animation-delay: 1.5s;
  animation-duration: 2.8s;
}

/* 애니메이션 키프레임 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes small-particle-float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0.6;
  }
  25% {
    transform: translateY(-8px) translateX(3px);
    opacity: 1;
  }
  50% {
    transform: translateY(-4px) translateX(-2px);
    opacity: 0.8;
  }
  75% {
    transform: translateY(-10px) translateX(4px);
    opacity: 0.9;
  }
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .small-alert-container {
    width: 250px;
    margin: 10px;
  }

  .small-alert-content {
    padding: 1rem 1.25rem;
  }

  .small-alert-title {
    font-size: 1rem;
  }

  .small-alert-message {
    font-size: 0.8rem;
  }
}

/* 다크모드 대응 */
@media (prefers-color-scheme: dark) {
  .small-alert-bg {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.4) 0%, rgba(20, 20, 20, 0.2) 100%);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .small-alert-title {
    background: linear-gradient(135deg, #f7fafc 0%, #e2e8f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .small-alert-message {
    color: #e2e8f0;
  }
}
</style>