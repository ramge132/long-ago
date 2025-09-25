<template>
  <div
    class="absolute top-[-60px] left-1/2 transform -translate-x-1/2 flex gap-x-1 w-64 h-14 p-1 rounded-full bg-[#ffffff80] backdrop-blur-sm"
  >
    <ContentTimer @next-turn="nextTurn" :currTurnTime="roomConfigs.currTurnTime" :inProgress="inProgress" :peerId="peerId" ref="timerRef" />
    <ContentGuage
      :percentage="percentage"
    />
  </div>
</template>
<script setup>
import { ref } from "vue";
import { ContentTimer, ContentGuage } from "@/components";

const emit = defineEmits(["nextTurn"]);
const nextTurn = (data) => {
  emit("nextTurn", data);
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
  peerId: {
    Type: String,
  },
});

// 타이머 ref 추가
const timerRef = ref(null);

// 외부에서 타이머 업데이트 가능하도록 expose
defineExpose({
  updateTimer: (newTime) => {
    if (timerRef.value) {
      timerRef.value.updateTimerFromPeer(newTime);
    }
  }
});

</script>
<style></style>
