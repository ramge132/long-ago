<template>
  <div
    class="absolute top-[-60px] left-1/2 transform -translate-x-1/2 flex gap-x-1 w-64 h-14 p-1 rounded-full bg-[#ffffff80] backdrop-blur-sm"
  >
    <ContentTimer @next-turn="nextTurn" :currTurnTime="roomConfigs.currTurnTime" :inProgress="inProgress" />
    <ContentGuage
      :percentage="percentage"
    />
  </div>
</template>
<script setup>
import { ContentTimer, ContentGuage } from "@/components";

const emit = defineEmits(["nextTurn"]);
const nextTurn = () => {
  emit("nextTurn");
};

const props = defineProps({
  roomConfigs: {
    Type: Object,
  },
  inProgress: {
    Type: Boolean,
  },
  percentage: {
    Type: Number,
  },
});

</script>
<style></style>
