<template>
  <div class="absolute w-full h-full rounded-lg bg-gradient-to-br from-black/20 via-black/15 to-black/20 flex justify-center">
    
    <!-- 메인 투표 패널 -->
    <div class="w-1/2 max-w-2xl h-2/3 bg-gradient-to-br from-white/95 to-white/85 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 flex flex-col items-center p-6 gap-4 z-20 relative overflow-hidden" 
         :class="voteEnded ? 'bounce-reverse' : 'bounce'" 
         @animationend="handleAnimationEnd">
      
      
      <!-- 모던한 프로그레스 바 -->
      <div class="modern-progress-container w-full h-6 mb-4">
        <div class="modern-progress-bar h-full rounded-full overflow-hidden bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300 shadow-inner border-2 border-gray-300">
          <div class="modern-progress-fill h-full bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 shadow-lg relative" 
               :class="countStarted ? 'animate-decrease' : 'w-full'" 
               :style="{ animationDuration: duration + 's' }" 
               @animationend="voteEnd">
            <div class="progress-shine absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-12 animate-shine"></div>
          </div>
        </div>
      </div>
      
      <!-- 질문 텍스트 -->
      <div class="text-center relative z-10">
        <h2 class="text-2xl lg:text-3xl font-katuri bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 bg-clip-text text-transparent drop-shadow-sm mb-2 leading-tight px-4">
          {{ usedCard.isEnding ? '이 이야기로 끝맺을까요?' : '이 이야기를 추가할까요?' }}
        </h2>
        <div class="w-16 h-1 bg-gradient-to-r from-orange-300 to-amber-400 rounded-full mx-auto"></div>
      </div>
      
      <!-- 프롬프트 박스 -->
      <div class="w-full bg-gradient-to-br from-gray-50 to-white border border-gray-200/50 rounded-2xl p-4 shadow-inner backdrop-blur-sm relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-blue-50/20 via-transparent to-purple-50/20 rounded-2xl"></div>
        <p class="text-lg lg:text-xl text-gray-700 font-medium leading-relaxed text-center relative z-10 break-words">{{ prompt }}</p>
      </div>
      
      <!-- 카드 슬롯 투표 버튼들 -->
      <div class="grid grid-cols-2 w-full h-full gap-6 mt-2">
        <!-- 찬성 카드 슬롯 -->
        <div class="card-slot cursor-pointer h-full"
             @click="selectVote('up')"
             :class="selected === 'up' ? 'selected' : ''"
             style="perspective: 1000px;">
          <div class="card-inner relative w-full h-full transition-transform duration-400 ease-out"
               style="transform-style: preserve-3d;"
               :style="{ transform: selected === 'up' ? 'rotateY(180deg) translateZ(10px)' : '' }">
            <!-- 카드 앞면 (기본 상태) -->
            <div class="card-face card-front absolute w-full h-full rounded-2xl flex flex-col justify-center items-center gap-3"
                 style="backface-visibility: hidden;">
              <img :src="VoteUpLeftIcon" alt="찬성" class="w-16 h-16 opacity-75">
              <span class="font-katuri text-lg font-bold text-gray-500">찬성</span>
            </div>
            <!-- 카드 뒷면 (선택된 상태) -->
            <div class="card-face card-back card-back-green absolute w-full h-full rounded-2xl flex flex-col justify-center items-center gap-3"
                 style="backface-visibility: hidden; transform: rotateY(180deg);">
              <img :src="VoteUpLeftIcon" alt="찬성" class="w-16 h-16 brightness-110">
              <span class="font-katuri text-lg font-bold text-white drop-shadow-md">선택됨!</span>
            </div>
          </div>
        </div>

        <!-- 반대 카드 슬롯 -->
        <div class="card-slot cursor-pointer h-full"
             @click="selectVote('down')"
             :class="selected === 'down' ? 'selected' : ''"
             style="perspective: 1000px;">
          <div class="card-inner relative w-full h-full transition-transform duration-400 ease-out"
               style="transform-style: preserve-3d;"
               :style="{ transform: selected === 'down' ? 'rotateY(180deg) translateZ(10px)' : '' }">
            <!-- 카드 앞면 (기본 상태) -->
            <div class="card-face card-front absolute w-full h-full rounded-2xl flex flex-col justify-center items-center gap-3"
                 style="backface-visibility: hidden;">
              <img :src="VoteDownRightIcon" alt="반대" class="w-16 h-16 opacity-75">
              <span class="font-katuri text-lg font-bold text-gray-500">반대</span>
            </div>
            <!-- 카드 뒷면 (선택된 상태) -->
            <div class="card-face card-back card-back-red absolute w-full h-full rounded-2xl flex flex-col justify-center items-center gap-3"
                 style="backface-visibility: hidden; transform: rotateY(180deg);">
              <img :src="VoteDownRightIcon" alt="반대" class="w-16 h-16 brightness-110">
              <span class="font-katuri text-lg font-bold text-white drop-shadow-md">선택됨!</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 사용한 카드 패널 -->
    <div class="bg-gradient-to-br from-white/90 to-white/75 backdrop-blur-xl rounded-2xl shadow-xl border border-white/30 flex flex-col translate-y-1/2 items-center p-6 ml-4 transition-all duration-1000 ease-in-out relative overflow-hidden min-h-[280px]" 
         :class="showCard ? '' : '-translate-x-[120%] opacity-0 z-0'"
         :style="{ height: cardPanelHeight + 'px' }">
      
      
      <div class="relative z-10">
        <p class="font-omp text-lg font-semibold text-gray-700 mb-3 text-center transition-opacity duration-300"
           :class="fontLoaded ? 'opacity-100' : 'opacity-0'">
           {{ usedCard.isFreeEnding ? '자유 결말' : '사용한 카드' }}
        </p>
        <div class="relative transform hover:scale-105 transition-transform duration-300" ref="cardRef">
          <!-- 엔딩 카드는 이미지로 표시, 스토리 카드는 개별 이미지 -->
          <template v-if="usedCard.isEnding">
            <img :src="CardImage.getEndingCardImage(usedCard.id)"
                 :alt="`엔딩카드 ${usedCard.id}`"
                 class="w-32 drop-shadow-lg">
            <!-- 카드 글로우 효과 -->
            <div class="absolute inset-0 bg-gradient-to-br from-amber-400/20 to-orange-500/10 rounded-lg blur-sm -z-10"></div>
          </template>
          <template v-else>
            <img :src="CardImage.getStoryCardImage(usedCard.id)"
                 :alt="`스토리카드 ${usedCard.keyword}`"
                 class="w-32 drop-shadow-lg">
            <!-- 카드 글로우 효과 -->
            <div class="absolute inset-0 bg-gradient-to-br from-amber-400/20 to-orange-500/10 rounded-lg blur-sm -z-10"></div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { VoteUpLeftIcon, VoteDownRightIcon } from '@/assets';
import CardImage from "@/assets/cards";
import { ref, onMounted, nextTick, watch } from 'vue';
import { useUserStore } from '@/stores/auth';
const userStore = useUserStore();
const selected = ref("up");
const countStarted = ref(false);
const voteEnded = ref(false);
const showCard = ref(false);
const cardRef = ref(null);
const contentRef = ref(null);
const contentSizes = ref([24, 20, 18, 16, 14, 12]); // px 단위로 변경
const duration = ref(10);
const fontLoaded = ref(false);
const cardPanelHeight = ref(280);
const currentFontSize = ref(24);
const emit = defineEmits(['voteEnd', 'voteSelected']);
const startCount = () => {
  countStarted.value = true;
};

const selectVote = (voteType) => {
  // 이미 선택된 것을 다시 클릭해도 선택 상태 유지
  if (selected.value !== voteType) {
    selected.value = voteType;
    // 부모 컴포넌트에 선택 값 전달
    emit('voteSelected', voteType);
  }
};
const props = defineProps({
  prompt: {
    Type: String,
  },
  usedCard: {
    Type: Object,
  },
  isPreview: {
    Type: Boolean,
  },
})
const voteEnd = () => {
  showCard.value = false;
  setTimeout(() => {
    voteEnded.value = true;
  }, 500);
};
const removeComponent = () => {
  const voteData = {
    sender: userStore.userData.userNickname,
    selected: selected.value
  };
  emit('voteEnd', voteData);
}
const handleAnimationEnd = (event) => {
  const animName = event.animationName;
  if (animName.includes("bounce-reverse")) {
    removeComponent();
  } 
  else if (animName.includes("bounce")) {
    startCount();
    showCard.value = true;
  }
};

const adjustCardSize = async () => {
  await nextTick();
  if(contentRef.value && cardRef.value) {
    let index = 0;
    currentFontSize.value = contentSizes.value[index];
    
    // 텍스트 크기를 줄여가며 카드 안에 맞도록 조정
    while(contentRef.value.scrollHeight > cardRef.value.clientHeight && index < contentSizes.value.length - 1) {
      index++;
      currentFontSize.value = contentSizes.value[index];
      await nextTick(); // DOM 업데이트 대기
    }
    
    // 가장 작은 폰트로도 텍스트가 넘치면 카드 패널 높이를 늘림
    if(contentRef.value.scrollHeight > cardRef.value.clientHeight) {
      const overflow = contentRef.value.scrollHeight - cardRef.value.clientHeight;
      cardPanelHeight.value = 280 + overflow + 60; // 기본 높이 + 오버플로우 + 여유 공간
    } else {
      cardPanelHeight.value = 280; // 기본 높이로 리셋
    }
  }
};

// 카드 내용 변경 시 크기 재조정
watch(() => props.usedCard.keyword, async () => {
  await adjustCardSize();
}, { deep: true });

// 새로운 투표 시작 시 모든 상태 초기화
watch(() => props.prompt, () => {
  if (props.prompt) {
    // 모든 상태를 초기값으로 리셋
    selected.value = "up";
    countStarted.value = false;
    voteEnded.value = false;
    showCard.value = false;
    cardPanelHeight.value = 280;
    currentFontSize.value = 24;
    duration.value = 10;
    
    // 기본값을 부모 컴포넌트에 알림
    emit('voteSelected', "up");
  }
});

onMounted(async () => {
  // 폰트 로딩 감지
  try {
    await document.fonts.load('400 18px omp');
    fontLoaded.value = true;
  } catch (error) {
    // 폰트 로딩 실패 시에도 표시 (fallback 폰트 사용)
    setTimeout(() => {
      fontLoaded.value = true;
    }, 200);
  }

  await adjustCardSize();
  // 진입 바운스 애니메이션(0.6초) 후 실제 투표시간 9초 + 퇴장 애니메이션(0.4초) = 총 10초
  duration.value = 9;

  // 마운트 시 기본값을 부모 컴포넌트에 알림
  emit('voteSelected', "up");
});

</script>
<style scoped>
/* 모던한 프로그레스 바 애니메이션 */
@keyframes animate-decrease {
  from { width: 100%; }
  to { width: 0; }
}

.animate-decrease {
  animation: animate-decrease linear forwards;
}

/* 반짝이는 효과 애니메이션 */
@keyframes animate-shine {
  0% { transform: translateX(-100%) skewX(12deg); }
  100% { transform: translateX(200%) skewX(12deg); }
}

.animate-shine {
  animation: animate-shine 2s infinite;
}

/* 부드러운 바운스 애니메이션 (개선된 버전) */
@keyframes bounce {
  0% {
    transform: scale(0) rotate(-12deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.05) rotate(3deg);
    opacity: 0.9;
  }
  80% {
    transform: scale(0.98) rotate(-1deg);
    opacity: 1;
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

@keyframes bounce-reverse {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  20% {
    transform: scale(1.05) rotate(-3deg);
    opacity: 0.9;
  }
  100% {
    transform: scale(0) rotate(12deg);
    opacity: 0;
  }
}

.bounce {
  animation: bounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.bounce-reverse {
  animation: bounce-reverse 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* 투표 버튼 호버 효과 */
.vote-button:not(.selected) {
  opacity: 0.85;
}

.vote-button.selected {
  opacity: 1;
}

.vote-button:not(.selected):hover {
  opacity: 1;
}

/* 카드 슬롯 스타일 */
.card-slot {
  position: relative;
  height: 100%;
}

.card-inner {
  border-radius: 16px;
}

.card-face {
  border-radius: 16px;
  font-weight: 600;
  font-size: 1.1rem;
}

.card-front {
  background: linear-gradient(145deg, #f3f4f6, #e5e7eb);
  color: #6b7280;
  border: 2px solid #d1d5db;
}

.card-back-green {
  background: linear-gradient(145deg, #10b981, #059669);
  color: white;
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.card-back-red {
  background: linear-gradient(145deg, #ef4444, #dc2626);
  color: white;
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

/* 카드 슬롯 호버 효과 */
.card-slot:hover .card-inner {
  transform: translateZ(5px);
}

.card-slot.selected:hover .card-inner {
  transform: rotateY(180deg) translateZ(15px) !important;
}

/* 투표 버튼 기본 스타일 */
.vote-button:not(.selected) {
  opacity: 0.85;
}

.vote-button.selected {
  opacity: 1;
}

.vote-button:not(.selected):hover {
  opacity: 1;
}

/* 부드러운 펄스 애니메이션 */
@keyframes animate-pulse-soft {
  0%, 100% { 
    opacity: 0.4;
    transform: scale(0.98);
  }
  50% { 
    opacity: 0.8;
    transform: scale(1.02);
  }
}

.animate-pulse-soft {
  animation: animate-pulse-soft 3s ease-in-out infinite;
}

/* 선택된 버튼의 추가 효과 */
.vote-button.selected {
  z-index: 10;
}

/* 프로그레스 바 컨테이너 */
.modern-progress-container {
  position: relative;
}

.modern-progress-bar {
  position: relative;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.modern-progress-fill {
  position: relative;
  transition: width 0.3s ease;
}


/* 카드 텍스트 그림자 효과 - 핸드 카드와 동일 */
.storycard {
  text-shadow: -1px 0px #9f876a, 0px 1px #9f876a, 1px 0px #9f876a, 0px -1px #9f876a;
}

.endingcard {
  text-shadow: -1px 0px #8a622a, 0px 1px #8a622a, 1px 0px #8a622a, 0px -1px #8a622a;
}

/* 프로그레스 바 컨테이너 */
.modern-progress-container {
  position: relative;
}

.modern-progress-bar {
  position: relative;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.modern-progress-fill {
  position: relative;
  transition: width 0.3s ease;
}

/* 글래스모피즘 효과를 위한 추가 스타일 */
.backdrop-blur-xl {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .text-2xl.lg\:text-3xl {
    font-size: 1.5rem;
  }
  
  .vote-button .w-16 {
    width: 3rem;
    height: 3rem;
  }
  
  .text-lg.lg\:text-xl {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .text-2xl.lg\:text-3xl {
    font-size: 1.25rem;
    line-height: 1.3;
  }
}

/* 접근성을 위한 포커스 스타일 */
.vote-button:focus-within {
  outline: 2px solid rgba(59, 130, 246, 0.5);
  outline-offset: 2px;
}

/* 터치 디바이스를 위한 탭 하이라이트 제거 */
.vote-button {
  -webkit-tap-highlight-color: transparent;
}
</style>