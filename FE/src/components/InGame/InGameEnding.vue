<template>
    <div class="absolute z-50 w-full h-full flex justify-center items-center bg-[#00000095] backdrop-blur-md">
        <div v-if="props.isForceStopped === 'champ'">
            <img src="@/assets/result.gif" alt="결과" class="w-full h-full">
            <div>
                <img :src="topParticipant.image" class="absolute bottom-1/3 left-1/2 -translate-x-1/2 translate-y-8 w-36 h-36" alt="">
                <div class="winner absolute top-3/4 left-1/2 -translate-x-1/2 font-katuri text-[#f1f1f1] text-6xl">
                    {{ topParticipant ? topParticipant.name : '결과 없음' }}
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { computed } from "vue";

const props = defineProps({
    participants: {
        Type: Array,
    },
    isForceStopped: {
        Type: String,
    },
});

// 가장 높은 점수를 가진 참가자 찾기
const topParticipant = computed(() => {
    if (!props.participants.length) return null;
    return props.participants.reduce((max, participant) => 
        participant.score > max.score ? participant : max
    );
});
</script>
<style scoped>
.winner {
  text-shadow: -2.5px 0px #2b87dc, 0px 2.5px #2b87dc, 2.5px 0px #2b87dc, 0px -2.5px #2b87dc;
}
</style>