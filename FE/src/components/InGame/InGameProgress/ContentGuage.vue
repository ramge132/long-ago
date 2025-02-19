<template>
  <div class="flex flex-1 flex-col items-center justify-center gap-y-2">
    <div class="w-5/6 flex justify-between">
      <!-- 긴장감 텍스트 -->
      <div class="text-gray-800 font-semibold text-sm">긴장감</div>
      <!-- 퍼센트 표시 -->
      <div class="text-gray-800 text-sm">{{ percentage }}%</div>
    </div>

    <!-- 게이지 바 -->
    <div class="h-3 w-5/6 bg-gray-300 rounded-full relative overflow-hidden">
      <div class="absolute z-10 w-[2px] h-4 bg-[#00000040] left-[35%] top-0 -translate-x-1/2"></div>
      <div
        class="absolute top-0 left-0 h-full rounded-full max-w-full transition-all duration-300"
        :class="gaugeColor"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from "vue";

const props = defineProps({
  percentage: {
    Type: Number,
  },
})

// 게이지 색상 계산
const gaugeColor = computed(() => {
  if (props.percentage <= 25) return "bg-green-500";
  if (props.percentage <= 50) return "bg-yellow-500";
  if (props.percentage <= 75) return "bg-orange-500";
  return "bg-red-500";
});
</script>

<style scoped></style>
