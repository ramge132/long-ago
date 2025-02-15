<template>
  <div
    class="w-4/5 max-w-6xl min-w-[1000px] h-16 py-2 flex justify-between items-center z-10"
  >
    <div
      class="w-full h-full rounded-lg bg-[#00000080] flex items-center justify-between px-4 text-white"
    >
      <div class="font-semibold" @click="emit('toggleTerms')">이용약관</div>
      <div>B101 | 김동휘 | 김형표 | 유태영 | 이세중 | 홍석진 | 홍정표</div>
      <div class="font-semibold text-xs">&copy; 2025. LONG AGO All rights reserved.</div>
    </div>
  </div>
</template>
<script setup>
  const emit = defineEmits(["toggleTerms"]);
</script>
