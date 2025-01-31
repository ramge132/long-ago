<template>
  <div
    class="absolute top-[-120px] w-52 h-48 bg-[#00000050] rounded-full flex flex-col items-center justify-center"
  >
    <div class="text-6xl mt-28 text-white">{{ restTime }}</div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";

const restTime = ref(20); // 초기 시간 설정
const startCountdown = () => {
  const timer = setInterval(() => {
    if (restTime.value > 0) {
      restTime.value--;
    } else {
      clearInterval(timer); // 카운트다운 종료 시 타이머 중지
    }
  }, 1000); // 1초 간격으로 감소
};

onMounted(() => {
  startCountdown(); // 컴포넌트가 마운트되면 카운트다운 시작
});
</script>
<style scoped></style>
