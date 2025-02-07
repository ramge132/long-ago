<template>
  <div
    class="absolute w-full h-full bg-[#00000050] flex justify-center items-center"
  >
    <div class="w-2/3 h-5/6 bg-[#ffffffdd] rounded-xl flex flex-col items-center p-3 gap-3">
      <p>시간 바</p>
      <p class="text-6xl">이 이야기를 추가할까요?</p>
      <div class="border-2 border-black w-full rounded-md flex justify-center items-center h-32">
        <p>프롬프트 메세지</p>
      </div>
      <div class="grid grid-cols-2 w-full h-full gap-4">
        <div class="border-4 border-black rounded-xl flex justify-center items-center cursor-pointer" @click="selected = 0" :class="selected === 0 ? 'border-green-400' : 'opacity-60'">
          <img :src="VoteUpLeftIcon" alt="따봉" class="w-3/5">
        </div>
        <div class="border-4 border-black rounded-xl flex justify-center items-center cursor-pointer" @click="selected = 1" :class="selected === 1 ? 'border-green-400' : 'opacity-60'">
          <img :src="VoteDownRightIcon" alt="역따봉" class="w-3/5">
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { VoteUpLeftIcon, VoteDownRightIcon } from '@/assets';
import { ref } from 'vue';
const selected = ref(-1);

</script>
<style></style>
