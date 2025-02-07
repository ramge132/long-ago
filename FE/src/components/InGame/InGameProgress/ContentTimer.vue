<template>
  <div
    :class="[
      'w-12 h-12 bg-[#00000080] rounded-full flex flex-col items-center justify-center',
      timeWarningClass,
    ]"
    style="box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3)"
  >
    <div class="text-xl text-white">{{ restTime }}</div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, watch } from "vue";

const emit = defineEmits(["nextTurn"]);
const props = defineProps({
  currTurnTime: {
    Type: Number,
  },
  inProgress: {
    Type: Boolean,
  },
})
const timer = ref(null);
const restTime = ref(0); // 초기 시간 설정
const timeWarningClass = ref(""); // 경고 상태를 위한 클래스
let worker = null; // Web Worker를 저장할 변수

const initCountdown = () => {
  restTime.value = props.currTurnTime;
}

// Web Worker 초기화 및 타이머 시작
const startCountdown = () => {
  // Worker가 없으면 새로 생성
  if (!worker) {
    worker = new Worker(new URL('@/functions/worker.js', import.meta.url));
  }
  // Web Worker에 초기 시간 전달
  worker.postMessage({ initialTime: props.currTurnTime });

  // Web Worker에서 메시지 받기
  worker.onmessage = (e) => {
    if (e.data === 'done') {
      emit('nextTurn'); // 타이머가 종료되면 'nextTurn' 이벤트 발생
    } else {
      restTime.value = e.data; // 남은 시간 업데이트
    }
  };
};


// restTime 값 변경을 감지하여 경고 상태 처리
watch(restTime, (newTime) => {
  if (newTime <= 5) {
    timeWarningClass.value = "bg-red-500 animate-blink"; // 5초 이하일 때 빨간색 깜빡이기
  } else {
    timeWarningClass.value = ""; // 5초 이상이면 기본 배경
  }
});

watch(() => props.inProgress, () => {
  if(props.inProgress) {
    startCountdown();
  } else {
    initCountdown();
    if (worker) {
        worker.postMessage('reset'); // Web Worker에 초기화 명령 보내기
    }
  }
}, {immediate: true});

// Web Worker 종료
onUnmounted(() => {
  if (worker) {
    worker.terminate(); // 컴포넌트가 파괴될 때 Worker 종료
  }
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
