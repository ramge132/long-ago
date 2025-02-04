<template>
  <div
    :class="['w-12 h-12 bg-[#00000080] rounded-full flex flex-col items-center justify-center', timeWarningClass]"
    style="box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);"
  >
    <div class="text-xl text-white">{{ restTime }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const emit = defineEmits(["nextTurn"]);
const restTime = ref(5); // 초기 시간 설정
const timeWarningClass = ref(''); // 경고 상태를 위한 클래스

// 타이머 시작
const startCountdown = () => {
  const timer = setInterval(() => {
    if (restTime.value > 0) {
      restTime.value--;
    } else {
      emit("nextTurn");
      restTime.value = 5;
      // clearInterval(timer); // 카운트다운 종료 시 타이머 중지
    }
  }, 1000); // 1초 간격으로 감소
};

// restTime 값 변경을 감지하여 경고 상태 처리
watch(restTime, (newTime) => {
  if (newTime <= 5) {
    timeWarningClass.value = 'bg-red-500 animate-blink'; // 5초 이하일 때 빨간색 깜빡이기
  } else {
    timeWarningClass.value = ''; // 5초 이상이면 기본 배경
  }
});

onMounted(() => {
  startCountdown(); // 컴포넌트가 마운트되면 카운트다운 시작
});
</script>

<style scoped>
/* 깜빡이는 애니메이션 */
@keyframes blink {
  0% {
    background-color: rgba(255, 0, 0, 0.5);
  }
  50% {
    background-color: rgba(255, 0, 0, 0.8);
  }
  100% {
    background-color: rgba(255, 0, 0, 0.5);
  }
}

.animate-blink {
  animation: blink 1s infinite;
}
</style>
