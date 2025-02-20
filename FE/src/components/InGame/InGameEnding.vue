<template>
    <div class="absolute z-50 w-full h-full flex justify-center items-center bg-[#00000095] backdrop-blur-md rounded-lg">
        <div v-if="props.isForceStopped === 'champ'" class="w-full h-full">
            <img src="@/assets/result_champ.gif" alt="결과" class="w-full h-full rounded-lg">
            <div class="flex gap-x-8 absolute left-1/2 -translate-x-1/2 bottom-32">
                <div v-for="topParticipant of topParticipants" class="flex flex-col justify-center items-center">
                    <img :src="topParticipant.image" class="w-36 h-36" alt="">
                    <div class="winner font-katuri text-[#f1f1f1] text-4xl">
                        {{ topParticipant ? topParticipant.name : '결과 없음' }}
                    </div>
                </div>
            </div>
        </div>
        <div v-else-if="props.isForceStopped === 'fail'" class="w-full h-full">
            <img src="@/assets/result_fail.gif" alt="결과" class="w-full h-full">
            <div class="loser absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-6xl font-katuri text-[#e0e0e0]">
                전원 실패!
            </div>
        </div>
    </div>
</template>
<script setup>
import { computed, watch } from "vue";
import { useAudioStore } from "@/stores/audio";
import { WinningMusic, LoseMusic } from "@/assets";

const audioStore = useAudioStore();
const winningMusic = new Audio(WinningMusic);
const loseMusic = new Audio(LoseMusic);

const props = defineProps({
    participants: {
        Type: Array,
    },
    isForceStopped: {
        Type: String,
    },
});

// 가장 높은 점수를 가진 참가자 찾기
const topParticipants = computed(() => {
  if (!props.participants.length) return [];
  
  // 참가자들의 점수 중 최댓값을 구합니다.
  const maxScore = Math.max(...props.participants.map(p => p.score));
  
  // 점수가 최댓값과 같은 참가자들을 필터링합니다.
  return props.participants.filter(p => p.score === maxScore);
});

watch(() => props.isForceStopped, () => {
    if (audioStore.audioData) {
        if (props.isForceStopped === "champ") {
            winningMusic.play();
            audioStore.audioPlay = false;
        } else if (props.isForceStopped === "fail") {
            loseMusic.play();
            audioStore.audioPlay = false;
        } else {
            audioStore.audioPlay = true;
            winningMusic.pause();
            loseMusic.pause();
            winningMusic.currentTime = 0
            loseMusic.currentTime = 0
        }
    }
});
</script>
<style scoped>
.winner {
    text-shadow: -2.5px 0px #2b87dc, 0px 2.5px #2b87dc, 2.5px 0px #2b87dc, 0px -2.5px #2b87dc;
}
.loser {
    text-shadow: -2.5px 0px #777777, 0px 2.5px #777777, 2.5px 0px #777777, 0px -2.5px #777777;
}
</style>