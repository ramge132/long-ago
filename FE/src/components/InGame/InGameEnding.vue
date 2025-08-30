<template>
    <div class="absolute z-50 w-full h-full flex justify-center items-center bg-[#00000095] backdrop-blur-md rounded-lg">
        <div v-if="props.isForceStopped === 'champ'" class="w-full h-full">
            <img src="@/assets/result_champ.gif" alt="결과" class="w-full h-full rounded-lg" ref="champGif" @load="onGifLoad">
            <div class="flex gap-x-8 absolute left-1/2 -translate-x-1/2 bottom-32">
                <div v-for="topParticipant of topParticipants" class="flex flex-col justify-center items-center">
                    <img :src="topParticipant.image" class="w-36 h-36" alt="">
                    <div class="winner font-katuri text-[#f1f1f1] text-4xl">
                        {{ topParticipant ? topParticipant.name : '결과 없음' }}
                    </div>
                </div>
            </div>
            <div class="absolute bottom-16 left-1/2 -translate-x-1/2 text-center">
                <div class="narration-text font-katuri text-[#f1f1f1] text-3xl">
                    이어서 책을 읽어드리겠습니다
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
import { computed, watch, ref } from "vue";
import { useAudioStore } from "@/stores/audio";
import { WinningMusic, LoseMusic } from "@/assets";

const audioStore = useAudioStore();
const winningMusic = new Audio(WinningMusic);
const loseMusic = new Audio(LoseMusic);
const champGif = ref(null);

const emit = defineEmits(['winner-shown']);

const props = defineProps({
    participants: {
        Type: Array,
    },
    isForceStopped: {
        Type: String,
    },
});

let gifDuration = 0;
let gifAnimationStartTime = 0;

const onGifLoad = () => {
    console.log('result_champ.gif loaded');
    
    // GIF 애니메이션 지속 시간을 측정하기 위한 로직
    // 일반적인 방법으로는 정확한 GIF 지속 시간을 얻기 어려우므로
    // 실제 테스트를 통해 확인된 값 사용
    
    // 테스트를 위해 애니메이션 시작 시간 기록
    gifAnimationStartTime = Date.now();
    
    // GIF가 반복되는 것을 감지하는 방법 (실험적)
    const img = champGif.value;
    if (img) {
        // 브라우저에서 GIF 애니메이션 완료를 감지하는 것은 직접적으로 불가능
        // 따라서 기존의 알려진 시간값을 사용하거나, 수동으로 측정해야 함
        console.log('GIF 이미지 요소:', img);
        
        // result_champ.gif의 실제 지속 시간을 확인하기 위한 타이머
        // (이 로그를 통해 실제 애니메이션이 언제 끝나는지 수동으로 확인 가능)
        for (let i = 1; i <= 15; i++) {
            setTimeout(() => {
                console.log(`🎬 result_champ.gif ${i}초 경과`);
            }, i * 1000);
        }
    }
};

// 가장 높은 점수를 가진 참가자 찾기
const topParticipants = computed(() => {
  if (!props.participants.length) return [];
  
  // 참가자들의 점수 중 최댓값을 구합니다.
  const maxScore = Math.max(...props.participants.map(p => p.score));
  
  // 점수가 최댓값과 같은 참가자들을 필터링합니다.
  return props.participants.filter(p => p.score === maxScore);
});

watch(() => props.isForceStopped, () => {
    if (props.isForceStopped === "champ") {
        // 음성이 켜져있을 때만 음악 재생
        if (audioStore.audioData) {
            winningMusic.play();
            audioStore.audioPlay = false;
        }
        
        // 결과창 표시 후 5초 대기한 다음 나레이션 시작 신호 전송 (sound off여도 실행)
        setTimeout(() => {
            emit('winner-shown');
        }, 5000);
        
    } else if (props.isForceStopped === "fail") {
        // 음성이 켜져있을 때만 음악 재생
        if (audioStore.audioData) {
            loseMusic.play();
            audioStore.audioPlay = false;
        }
    } else {
        if (audioStore.audioData) {
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
.narration-text {
    text-shadow: -2px 0px #333333, 0px 2px #333333, 2px 0px #333333, 0px -2px #333333;
    animation: fadeInUp 1s ease-in-out 2s both;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
