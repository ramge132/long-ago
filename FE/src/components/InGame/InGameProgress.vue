<template>
  <div
    class="absolute top-[-60px] left-1/2 transform -translate-x-1/2 flex gap-x-1 w-64 h-14 p-1 rounded-full bg-[#ffffff80] backdrop-blur-sm"
  >
    <ContentTimer @next-turn="nextTurn" />
    <ContentGuage />
  </div>
</template>
<script setup>
import { ContentTimer, ContentGuage } from "@/components";

const emit = defineEmits(["nextTurn"]);
const nextTurn = () => {
  emit("nextTurn");
};
</script>
<style></style>
