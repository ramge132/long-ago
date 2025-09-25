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
import { useGameStore } from "@/stores/game";

const emit = defineEmits(["nextTurn"]);
const props = defineProps({
  currTurnTime: {
    Type: Number,
  },
  inProgress: {
    Type: Boolean,
  },
  peerId: {
    Type: String,
  }
})

const gameStore = useGameStore();
const timer = ref(null);
const restTime = ref(0); // 초기 시간 설정
const timeWarningClass = ref(""); // 경고 상태를 위한 클래스
let worker = null; // Web Worker를 저장할 변수
let masterTimer = null; // 방장 전용 타이머

const initCountdown = () => {
  restTime.value = props.currTurnTime;
}

// 방장 전용: 마스터 타이머 시작 (실제 시간 관리)
const startMasterTimer = () => {
  if (masterTimer) {
    clearInterval(masterTimer);
  }

  let timeLeft = props.currTurnTime;
  restTime.value = timeLeft;

  console.log("🕰️ 방장 마스터 타이머 시작:", timeLeft, "초");

  masterTimer = setInterval(() => {
    timeLeft--;
    restTime.value = timeLeft;

    console.log("🕰️ 방장 타이머:", timeLeft, "초");

    if (timeLeft <= 0) {
      clearInterval(masterTimer);
      masterTimer = null;
      console.log("🕰️ 방장 타이머 만료 - nextTurn 이벤트 발생");
      emit('nextTurn', null); // 방장만 nextTurn 이벤트 발생 (타임아웃으로 인한 턴 넘김)
    }
  }, 1000);
};

// 게스트 전용: UI만 표시하는 더미 타이머
const startDisplayTimer = () => {
  // Worker가 없으면 새로 생성 (UI 표시용)
  if (!worker) {
    worker = new Worker(new URL('@/functions/worker.js', import.meta.url));
  }
  // Web Worker에 초기 시간 전달
  worker.postMessage({ initialTime: props.currTurnTime });

  // Web Worker에서 메시지 받기 (UI 업데이트만)
  worker.onmessage = (e) => {
    if (e.data !== 'done') {
      restTime.value = e.data; // 남은 시간 UI 업데이트만
    }
    // 게스트는 nextTurn 이벤트를 발생시키지 않음
  };
};

// 타이머 시작 결정
const startCountdown = () => {
  const isBoss = props.peerId === gameStore.getBossId();

  if (isBoss) {
    console.log("🎯 방장: 마스터 타이머 시작");
    startMasterTimer();
  } else {
    console.log("👥 게스트: 디스플레이 타이머 시작");
    startDisplayTimer();
  }
};


// restTime 값 변경을 감지하여 경고 상태 처리
watch(restTime, (newTime) => {
  if (newTime <= 5) {
    timeWarningClass.value = "bg-red-500 animate-blink"; // 5초 이하일 때 빨간색 깜빡이기
  } else {
    timeWarningClass.value = ""; // 5초 이상이면 기본 배경
  }
});

// 타이머 업데이트 함수 (P2P 메시지로 동기화)
const updateTimerFromPeer = (newTime) => {
  restTime.value = newTime;
};

// 외부에서 타이머 값을 설정하는 함수 (expose)
defineExpose({
  updateTimerFromPeer
});

watch(() => props.inProgress, () => {
  if(props.inProgress) {
    startCountdown();
  } else {
    initCountdown();

    // 타이머 정리
    if (masterTimer) {
      clearInterval(masterTimer);
      masterTimer = null;
    }
    if (worker) {
      worker.postMessage('reset'); // Web Worker에 초기화 명령 보내기
    }
  }
}, {immediate: true});

// 컴포넌트 정리
onUnmounted(() => {
  if (worker) {
    worker.terminate(); // 컴포넌트가 파괴될 때 Worker 종료
  }
  if (masterTimer) {
    clearInterval(masterTimer);
    masterTimer = null;
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
